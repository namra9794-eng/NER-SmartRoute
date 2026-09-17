import uuid
from django.conf import settings
from django.db import models
from roads.models import Road


class Incident(models.Model):
    """
    Geo-tagged field incident report (spec point f), submitted by field
    officials/local authorities, optionally offline-first and synced later.
    """

    class IncidentType(models.TextChoices):
        LANDSLIDE = "landslide", "Landslide"
        FLOOD = "flood", "Flood"
        HEAVY_RAINFALL = "heavy_rainfall", "Heavy Rainfall"
        ROAD_DAMAGE = "road_damage", "Road Damage"
        BRIDGE_DAMAGE = "bridge_damage", "Bridge Damage"
        TRAFFIC_CONGESTION = "traffic_congestion", "Traffic Congestion"
        OTHER = "other", "Other"

    class Severity(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    # client_uuid lets a mobile app generate the record offline and sync
    # later without creating duplicates (spec point h: offline sync).
    client_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="incidents"
    )
    road = models.ForeignKey(Road, on_delete=models.SET_NULL, null=True, blank=True, related_name="incidents")

    incident_type = models.CharField(max_length=30, choices=IncidentType.choices)
    description = models.TextField(blank=True)
    severity = models.CharField(max_length=20, choices=Severity.choices, default=Severity.MEDIUM)

    latitude = models.FloatField()
    longitude = models.FloatField()

    photo = models.ImageField(upload_to="incidents/%Y/%m/", null=True, blank=True)

    district_name = models.CharField(max_length=100, blank=True)
    resolved = models.BooleanField(default=False)

    occurred_at = models.DateTimeField(help_text="When the incident happened on the ground")
    synced_at = models.DateTimeField(auto_now_add=True, help_text="When the server received it")
    created_offline = models.BooleanField(default=False)

    class Meta:
        ordering = ["-occurred_at"]

    def __str__(self):
        return f"{self.get_incident_type_display()} @ ({self.latitude}, {self.longitude})"
