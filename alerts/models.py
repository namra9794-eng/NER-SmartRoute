from django.db import models
from roads.models import District, Road


class Alert(models.Model):
    """Automated + manual alerts (spec point e), with multilingual delivery (point h)."""

    class AlertType(models.TextChoices):
        BLOCKED_ROAD = "blocked_road", "Blocked Road"
        HIGH_RISK = "high_risk", "High Risk Corridor"
        VEHICLE_DELAY = "vehicle_delay", "Vehicle Delay"
        WEATHER = "weather", "Weather Alert"
        INACCESSIBLE_REGION = "inaccessible_region", "Inaccessible Region"

    class Severity(models.TextChoices):
        INFO = "info", "Info"
        WARNING = "warning", "Warning"
        CRITICAL = "critical", "Critical"

    alert_type = models.CharField(max_length=30, choices=AlertType.choices)
    severity = models.CharField(max_length=20, choices=Severity.choices, default=Severity.WARNING)

    title = models.CharField(max_length=255)
    message = models.TextField()

    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True, related_name="alerts")
    road = models.ForeignKey(Road, on_delete=models.SET_NULL, null=True, blank=True, related_name="alerts")

    is_auto_generated = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.severity}] {self.title}"


class AlertTranslation(models.Model):
    """Pre-translated copy for a supported language (spec point h: multilingual)."""
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name="translations")
    language_code = models.CharField(max_length=10)
    title = models.CharField(max_length=255)
    message = models.TextField()

    class Meta:
        unique_together = ["alert", "language_code"]
