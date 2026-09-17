from django.conf import settings
from django.db import models


class RouteRequest(models.Model):
    """Logged route-optimization queries, for analytics on frequent corridors."""
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="route_requests"
    )
    source_name = models.CharField(max_length=200)
    destination_name = models.CharField(max_length=200)
    source_latitude = models.FloatField()
    source_longitude = models.FloatField()
    destination_latitude = models.FloatField()
    destination_longitude = models.FloatField()

    fastest_time_minutes = models.FloatField(null=True, blank=True)
    safest_time_minutes = models.FloatField(null=True, blank=True)
    delay_minutes = models.FloatField(null=True, blank=True)
    recommended = models.CharField(max_length=10, default="safest", help_text="fastest | safest")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
