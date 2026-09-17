from rest_framework import serializers
from .models import RouteRequest


class RouteOptimizeRequestSerializer(serializers.Serializer):
    source_name = serializers.CharField(required=False, allow_blank=True, default="")
    destination_name = serializers.CharField(required=False, allow_blank=True, default="")
    source_latitude = serializers.FloatField()
    source_longitude = serializers.FloatField()
    destination_latitude = serializers.FloatField()
    destination_longitude = serializers.FloatField()


class RouteRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteRequest
        fields = "__all__"
        read_only_fields = ["requested_by", "created_at"]
