from django.urls import path
from .views import RouteOptimizeView, RouteRequestHistoryView

urlpatterns = [
    path("routes/optimize/", RouteOptimizeView.as_view(), name="route-optimize"),
    path("routes/history/", RouteRequestHistoryView.as_view(), name="route-history"),
]
