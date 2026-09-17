from rest_framework import serializers
from .models import WeatherRecord


class WeatherRecordSerializer(serializers.ModelSerializer):
    district_name = serializers.CharField(source="district.name", read_only=True)

    class Meta:
        model = WeatherRecord
        fields = "__all__"
        read_only_fields = ["recorded_at", "source"]
