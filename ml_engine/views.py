from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions

from roads.models import Road
from .risk_model import RiskInput, predict
from .serializers import RiskPredictionRequestSerializer


class RiskPredictionView(APIView):
    """
    POST /api/predictions/risk/
    {
        "rainfall_mm_24h": 82, "road_condition_score": 7,
        "previous_incidents_count": 4, "traffic_congestion_pct": 70
    }
    ->
    { "risk": "high", "probability": 0.87, "edge_cost_multiplier": 4.48 }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = RiskPredictionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        road_id = data.pop("road_id", None)

        result = predict(RiskInput(**data))

        if road_id:
            road = Road.objects.filter(pk=road_id).first()
            if road:
                road.risk_level = result["risk"]
                road.risk_probability = result["probability"]
                if result["risk"] == "critical":
                    road.status = Road.Status.BLOCKED
                elif result["risk"] == "high":
                    road.status = Road.Status.RISKY
                road.save()

        return Response(result)
