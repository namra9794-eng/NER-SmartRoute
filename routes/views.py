from rest_framework import permissions, status, generics
from rest_framework.response import Response
from rest_framework.views import APIView

from roads.serializers import RoadSerializer
from .graph_engine import RouteGraph
from .models import RouteRequest
from .serializers import RouteOptimizeRequestSerializer, RouteRequestSerializer


class RouteOptimizeView(APIView):
    """
    POST /api/routes/optimize/
    {
        "source_name": "Guwahati", "destination_name": "Itanagar",
        "source_latitude": 26.1445, "source_longitude": 91.7362,
        "destination_latitude": 27.0844, "destination_longitude": 93.6053
    }
    -> fastest route, safest (risk-aware) route, and the estimated delay
       between them (spec point c).
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = RouteOptimizeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data

        graph = RouteGraph()
        fastest = graph.shortest_path(
            d["source_latitude"], d["source_longitude"],
            d["destination_latitude"], d["destination_longitude"],
            avoid_risk=False,
        )
        safest = graph.shortest_path(
            d["source_latitude"], d["source_longitude"],
            d["destination_latitude"], d["destination_longitude"],
            avoid_risk=True,
        )

        if fastest is None and safest is None:
            return Response(
                {"detail": "No route found between the given points with the current road network."},
                status=status.HTTP_404_NOT_FOUND,
            )

        def serialize_route(route):
            if route is None:
                return None
            return {
                "roads": RoadSerializer(route["roads"], many=True).data,
                "distance_km": route["distance_km"],
                "estimated_travel_time_minutes": route["estimated_travel_time_minutes"],
                "max_risk_level": route["max_risk_level"],
                "passes_through_blocked_road": route["passes_through_blocked_road"],
            }

        delay_minutes = None
        if fastest and safest:
            delay_minutes = round(safest["estimated_travel_time_minutes"] - fastest["estimated_travel_time_minutes"], 1)

        recommended = "safest" if (fastest and fastest["passes_through_blocked_road"]) or not fastest else (
            "safest" if safest and safest["max_risk_level"] in ("low", "medium") else "fastest"
        )

        route_request = RouteRequest.objects.create(
            requested_by=request.user if request.user.is_authenticated else None,
            source_name=d.get("source_name", ""),
            destination_name=d.get("destination_name", ""),
            source_latitude=d["source_latitude"],
            source_longitude=d["source_longitude"],
            destination_latitude=d["destination_latitude"],
            destination_longitude=d["destination_longitude"],
            fastest_time_minutes=fastest["estimated_travel_time_minutes"] if fastest else None,
            safest_time_minutes=safest["estimated_travel_time_minutes"] if safest else None,
            delay_minutes=delay_minutes,
            recommended=recommended,
        )

        return Response({
            "request_id": route_request.id,
            "fastest_route": serialize_route(fastest),
            "safest_route": serialize_route(safest),
            "estimated_delay_minutes": delay_minutes,
            "recommended": recommended,
        })


class RouteRequestHistoryView(generics.ListAPIView):
    queryset = RouteRequest.objects.all()
    serializer_class = RouteRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
