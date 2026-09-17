from django.db import models
from roads.models import District


class WeatherRecord(models.Model):
    """Weather snapshot for a district, feeding the ML risk engine (spec point h)."""
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name="weather_records")
    rainfall_mm_24h = models.FloatField(default=0)
    rainfall_mm_72h = models.FloatField(default=0)
    temperature_celsius = models.FloatField(null=True, blank=True)
    condition = models.CharField(max_length=100, blank=True, help_text="e.g. Heavy Rain, Clear, Fog")
    forecast_next_24h = models.CharField(max_length=100, blank=True)
    source = models.CharField(max_length=50, default="manual", help_text="manual | api_sync | simulator")
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-recorded_at"]

    def __str__(self):
        return f"{self.district.name} @ {self.recorded_at:%Y-%m-%d %H:%M}"
