from rest_framework import serializers
from .models import Vehicle, VehicleLocationLog


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = "__all__"
        read_only_fields = ["updated_at"]


class VehiclePingSerializer(serializers.Serializer):
    """Body for POST /api/vehicles/{id}/ping/ — simulator or mobile GPS unit."""
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    speed_kmph = serializers.FloatField(default=0)
    heading_degrees = serializers.FloatField(default=0)
    recorded_at = serializers.DateTimeField(required=False)
    status = serializers.ChoiceField(choices=Vehicle.Status.choices, required=False)


class VehicleLocationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleLocationLog
        fields = "__all__"
