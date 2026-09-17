from django.urls import path
from .views import (
    ConnectivityStatusView, BottlenecksView, EmergencyRoutesView, LiveMovementView,
)

urlpatterns = [
    path("connectivity/", ConnectivityStatusView.as_view(), name="dashboard-connectivity"),
    path("bottlenecks/", BottlenecksView.as_view(), name="dashboard-bottlenecks"),
    path("emergency-routes/", EmergencyRoutesView.as_view(), name="dashboard-emergency-routes"),
    path("live-movement/", LiveMovementView.as_view(), name="dashboard-live-movement"),
]
