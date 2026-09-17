from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend

from alerts.services import raise_alert_for_incident
from roads.models import Road
from .models import Incident
from .serializers import IncidentSerializer


class IncidentViewSet(viewsets.ModelViewSet):
    """
    POST /api/incidents/   field officials upload geo-tagged reports (+ photo).
    Uses client_uuid for idempotent offline sync: resubmitting the same
    client_uuid updates rather than duplicates the record.
    """
    queryset = Incident.objects.select_related("reported_by", "road").all()
    serializer_class = IncidentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["incident_type", "severity", "resolved", "district_name", "road"]

    def get_queryset(self):
        return super().get_queryset()

    def perform_create(self, serializer):
        client_uuid = serializer.validated_data.get("client_uuid")
        existing = Incident.objects.filter(client_uuid=client_uuid).first() if client_uuid else None
        if existing:
            for field, value in serializer.validated_data.items():
                setattr(existing, field, value)
            existing.save()
            instance = existing
        else:
            instance = serializer.save(reported_by=self.request.user)

        # Escalate serious incidents: mark the affected road risky/blocked
        # and fan out an automated alert (spec point e).
        if instance.road and instance.severity in (
            Incident.Severity.HIGH, Incident.Severity.CRITICAL
        ):
            road = instance.road
            road.status = Road.Status.BLOCKED if instance.severity == Incident.Severity.CRITICAL else Road.Status.RISKY
            road.save(update_fields=["status", "last_updated"])
        raise_alert_for_incident(instance)
