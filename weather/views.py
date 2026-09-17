import requests
from django.conf import settings
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from roads.models import District
from .models import WeatherRecord
from .serializers import WeatherRecordSerializer


class WeatherRecordViewSet(viewsets.ModelViewSet):
    """
    GET  /api/weather/                       list records (filter by district)
    POST /api/weather/                       manual entry / simulator push
    POST /api/weather/sync/?district_id=..   pull live data from an external
                                              weather API (integration point).
    """
    queryset = WeatherRecord.objects.select_related("district").all()
    serializer_class = WeatherRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["district"]

    @action(detail=False, methods=["post"])
    def sync(self, request):
        district_id = request.query_params.get("district_id")
        district = District.objects.filter(pk=district_id).first() if district_id else None
        if not district:
            return Response({"detail": "district_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        if not settings.WEATHER_API_KEY:
            return Response(
                {"detail": "WEATHER_API_KEY not configured; use manual POST instead."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        resp = requests.get(
            f"{settings.WEATHER_API_BASE_URL}/weather",
            params={"lat": district.latitude, "lon": district.longitude, "appid": settings.WEATHER_API_KEY, "units": "metric"},
            timeout=10,
        )
        resp.raise_for_status()
        payload = resp.json()

        record = WeatherRecord.objects.create(
            district=district,
            rainfall_mm_24h=payload.get("rain", {}).get("1h", 0) * 24,
            temperature_celsius=payload.get("main", {}).get("temp"),
            condition=(payload.get("weather") or [{}])[0].get("main", ""),
            source="api_sync",
        )
        return Response(WeatherRecordSerializer(record).data, status=status.HTTP_201_CREATED)
