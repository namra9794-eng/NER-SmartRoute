from rest_framework import serializers
from .models import Alert, AlertTranslation


class AlertTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertTranslation
        fields = ["language_code", "title", "message"]


class AlertSerializer(serializers.ModelSerializer):
    translations = AlertTranslationSerializer(many=True, required=False)
    district_name = serializers.CharField(source="district.name", read_only=True)

    class Meta:
        model = Alert
        fields = "__all__"

    def create(self, validated_data):
        translations = validated_data.pop("translations", [])
        alert = Alert.objects.create(**validated_data)
        for t in translations:
            AlertTranslation.objects.create(alert=alert, **t)
        return alert
