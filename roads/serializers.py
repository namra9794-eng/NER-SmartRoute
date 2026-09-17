from rest_framework import serializers
from .models import District, Road


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = "__all__"


class RoadSerializer(serializers.ModelSerializer):
    district_name = serializers.CharField(source="district.name", read_only=True)

    class Meta:
        model = Road
        fields = "__all__"


class DistrictConnectivitySerializer(serializers.ModelSerializer):
    """Used by the dashboard: district-wise connectivity summary (spec point g)."""
    total_roads = serializers.IntegerField()
    open_roads = serializers.IntegerField()
    risky_roads = serializers.IntegerField()
    blocked_roads = serializers.IntegerField()
    connectivity_score = serializers.FloatField()

    class Meta:
        model = District
        fields = [
            "id", "name", "state", "latitude", "longitude",
            "total_roads", "open_roads", "risky_roads", "blocked_roads",
            "connectivity_score",
        ]
