"""
Centralized dashboard aggregation endpoints (spec point g):
  - district-wise connectivity status
  - logistics bottlenecks / supply-chain gaps
  - emergency / disaster-time accessibility routes
  - real-time movement & delivery status of essential supplies
"""
from django.db.models import Count, Q
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions

from alerts.models import Alert
from logistics.models import Shipment
from roads.models import District, Road
from vehicles.models import Vehicle


class ConnectivityStatusView(APIView):
    """GET /api/dashboard/connectivity/ — district-wise road status roll-up."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        districts = District.objects.annotate(
            total_roads=Count("roads"),
            open_roads=Count("roads", filter=Q(roads__status=Road.Status.OPEN)),
            risky_roads=Count("roads", filter=Q(roads__status=Road.Status.RISKY)),
            blocked_roads=Count("roads", filter=Q(roads__status=Road.Status.BLOCKED)),
        )
        results = []
        for d in districts:
            connectivity_score = (
                round((d.open_roads / d.total_roads) * 100, 1) if d.total_roads else 100.0
            )
            results.append({
                "id": d.id, "name": d.name, "state": d.state,
                "latitude": d.latitude, "longitude": d.longitude,
                "total_roads": d.total_roads, "open_roads": d.open_roads,
                "risky_roads": d.risky_roads, "blocked_roads": d.blocked_roads,
                "connectivity_score": connectivity_score,
                "status": (
                    "isolated" if d.total_roads and d.open_roads == 0
                    else "critical" if connectivity_score < 50
                    else "constrained" if connectivity_score < 85
                    else "normal"
                ),
            })
        return Response(results)


class BottlenecksView(APIView):
    """GET /api/dashboard/bottlenecks/ — supply-chain gaps & congested corridors."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        risky_roads = Road.objects.filter(
            status__in=[Road.Status.RISKY, Road.Status.BLOCKED]
        ).select_related("district").order_by("-risk_probability")[:25]

        delayed_shipments = Shipment.objects.exclude(
            delivery_status=Shipment.DeliveryStatus.DELIVERED
        ).select_related("vehicle")
        delayed_shipments = [s for s in delayed_shipments if s.is_delayed]

        return Response({
            "high_risk_or_blocked_roads": [
                {
                    "id": r.id, "name": r.name, "district": r.district.name,
                    "status": r.status, "risk_level": r.risk_level,
                    "risk_probability": r.risk_probability,
                }
                for r in risky_roads
            ],
            "delayed_shipments": [
                {
                    "reference_code": s.reference_code, "cargo_type": s.cargo_type,
                    "priority": s.priority, "destination": s.destination,
                    "estimated_arrival": s.estimated_arrival,
                    "vehicle_number": s.vehicle.vehicle_number if s.vehicle else None,
                }
                for s in delayed_shipments
            ],
            "active_critical_alerts": Alert.objects.filter(
                active=True, severity=Alert.Severity.CRITICAL
            ).count(),
        })


class EmergencyRoutesView(APIView):
    """GET /api/dashboard/emergency-routes/ — accessibility during disasters."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        open_roads = Road.objects.filter(status=Road.Status.OPEN).select_related("district")
        blocked_roads = Road.objects.filter(status=Road.Status.BLOCKED).select_related("district")
        return Response({
            "generated_at": timezone.now(),
            "usable_road_count": open_roads.count(),
            "blocked_road_count": blocked_roads.count(),
            "blocked_roads": [
                {"id": r.id, "name": r.name, "district": r.district.name}
                for r in blocked_roads
            ],
        })


class LiveMovementView(APIView):
    """GET /api/dashboard/live-movement/ — real-time fleet + delivery snapshot."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        vehicles = Vehicle.objects.all()
        shipments = Shipment.objects.exclude(delivery_status=Shipment.DeliveryStatus.DELIVERED)
        return Response({
            "vehicles": [
                {
                    "id": v.id, "vehicle_number": v.vehicle_number,
                    "cargo_type": v.cargo_type, "status": v.status,
                    "latitude": v.latitude, "longitude": v.longitude,
                    "destination": v.destination, "eta": v.eta,
                }
                for v in vehicles
            ],
            "active_shipments_count": shipments.count(),
        })
