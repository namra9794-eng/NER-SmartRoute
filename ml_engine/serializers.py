from rest_framework import serializers


class RiskPredictionRequestSerializer(serializers.Serializer):
    rainfall_mm_24h = serializers.FloatField(default=0)
    rainfall_mm_72h = serializers.FloatField(default=0)
    road_condition_score = serializers.FloatField(default=5, min_value=1, max_value=10)
    previous_incidents_count = serializers.IntegerField(default=0, min_value=0)
    traffic_congestion_pct = serializers.FloatField(default=0, min_value=0, max_value=100)
    landslide_prone = serializers.BooleanField(default=False)
    flood_prone = serializers.BooleanField(default=False)
    slope_gradient_deg = serializers.FloatField(default=0)
    road_id = serializers.IntegerField(required=False, help_text="If given, also updates Road.risk_level")
