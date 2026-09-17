from rest_framework import serializers
from .models import Incident


class IncidentSerializer(serializers.ModelSerializer):
    reported_by_username = serializers.CharField(source="reported_by.username", read_only=True)

    class Meta:
        model = Incident
        fields = "__all__"
        read_only_fields = ["synced_at", "reported_by"]

    def create(self, validated_data):
        validated_data["reported_by"] = self.context["request"].user
        return super().create(validated_data)
