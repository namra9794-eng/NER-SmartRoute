from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Vehicle, VehicleLocationLog
from .serializers import VehicleSerializer, VehiclePingSerializer, VehicleLocationLogSerializer


class VehicleViewSet(viewsets.ModelViewSet):
    """
    GET  /api/vehicles/                 live fleet positions for the map
    POST /api/vehicles/{id}/ping/       GPS update from device/simulator
    GET  /api/vehicles/{id}/history/    location trail
    """
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status", "cargo_type", "operator"]

    @action(detail=True, methods=["post"])
    def ping(self, request, pk=None):
        vehicle = self.get_object()
        serializer = VehiclePingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        vehicle.latitude = data["latitude"]
        vehicle.longitude = data["longitude"]
        vehicle.speed_kmph = data.get("speed_kmph", 0)
        vehicle.heading_degrees = data.get("heading_degrees", 0)
        if data.get("status"):
            vehicle.status = data["status"]
        vehicle.save()

        VehicleLocationLog.objects.create(
            vehicle=vehicle,
            latitude=data["latitude"],
            longitude=data["longitude"],
            speed_kmph=data.get("speed_kmph", 0),
            recorded_at=data.get("recorded_at") or timezone.now(),
        )
        return Response(VehicleSerializer(vehicle).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def history(self, request, pk=None):
        vehicle = self.get_object()
        logs = vehicle.location_logs.all()[:200]
        return Response(VehicleLocationLogSerializer(logs, many=True).data)
