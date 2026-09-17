from django.conf import settings
from django.db import models


class Vehicle(models.Model):
    """A logistics vehicle carrying essential commodities (spec point d)."""

    class Status(models.TextChoices):
        MOVING = "moving", "Moving"
        STOPPED = "stopped", "Stopped"
        DELAYED = "delayed", "Delayed"
        DELIVERED = "delivered", "Delivered"
        BREAKDOWN = "breakdown", "Breakdown"

    vehicle_number = models.CharField(max_length=50, unique=True)
    driver_name = models.CharField(max_length=150, blank=True)
    driver_phone = models.CharField(max_length=20, blank=True)
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="vehicles"
    )

    cargo_type = models.CharField(max_length=100, help_text="e.g. Medicine, Food, Construction Material")
    source = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)

    latitude = models.FloatField()
    longitude = models.FloatField()
    speed_kmph = models.FloatField(default=0)
    heading_degrees = models.FloatField(default=0)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.MOVING)
    eta = models.DateTimeField(null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.vehicle_number


class VehicleLocationLog(models.Model):
    """Append-only GPS ping history, also used to replay routes / detect delays."""
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="location_logs")
    latitude = models.FloatField()
    longitude = models.FloatField()
    speed_kmph = models.FloatField(default=0)
    recorded_at = models.DateTimeField()
    synced_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-recorded_at"]
