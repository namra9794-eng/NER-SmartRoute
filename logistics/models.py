from django.db import models
from vehicles.models import Vehicle


class Shipment(models.Model):
    """
    A consignment of essential goods moving between two points (spec point d/g):
    medicines, food supplies, agricultural produce, construction material.
    """

    class CargoType(models.TextChoices):
        MEDICINE = "medicine", "Medicine"
        FOOD = "food", "Food Supplies"
        AGRICULTURAL_PRODUCE = "agricultural_produce", "Agricultural Produce"
        CONSTRUCTION_MATERIAL = "construction_material", "Construction Material"
        OTHER = "other", "Other"

    class Priority(models.TextChoices):
        ROUTINE = "routine", "Routine"
        URGENT = "urgent", "Urgent"
        EMERGENCY = "emergency", "Emergency"

    class DeliveryStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_TRANSIT = "in_transit", "In Transit"
        DELAYED = "delayed", "Delayed"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    reference_code = models.CharField(max_length=50, unique=True)
    cargo_type = models.CharField(max_length=30, choices=CargoType.choices)
    description = models.CharField(max_length=255, blank=True)
    weight_kg = models.FloatField(null=True, blank=True)

    origin = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.ROUTINE)

    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name="shipments"
    )
    delivery_status = models.CharField(
        max_length=20, choices=DeliveryStatus.choices, default=DeliveryStatus.PENDING
    )

    scheduled_departure = models.DateTimeField(null=True, blank=True)
    estimated_arrival = models.DateTimeField(null=True, blank=True)
    actual_arrival = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.reference_code} ({self.get_cargo_type_display()})"

    @property
    def is_delayed(self):
        from django.utils import timezone
        return (
            self.delivery_status != self.DeliveryStatus.DELIVERED
            and self.estimated_arrival is not None
            and timezone.now() > self.estimated_arrival
        )
