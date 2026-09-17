from django.urls import path
from .views import RiskPredictionView

urlpatterns = [
    path("predictions/risk/", RiskPredictionView.as_view(), name="risk-prediction"),
]
