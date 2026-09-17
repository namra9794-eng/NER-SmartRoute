from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .models import District, Road
from .serializers import DistrictSerializer, RoadSerializer


class DistrictViewSet(viewsets.ModelViewSet):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["state"]


class RoadViewSet(viewsets.ModelViewSet):
    """
    GET  /api/roads/                 list, filterable by district/status/risk_level
    POST /api/roads/                 add a road segment
    PATCH /api/roads/{id}/           update status/risk (e.g. after an incident)
    """
    queryset = Road.objects.select_related("district").all()
    serializer_class = RoadSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["district", "status", "risk_level", "road_type"]
    search_fields = ["name"]
