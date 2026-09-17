from rest_framework.routers import DefaultRouter
from .views import DistrictViewSet, RoadViewSet

router = DefaultRouter()
router.register(r"districts", DistrictViewSet, basename="district")
router.register(r"roads", RoadViewSet, basename="road")

urlpatterns = router.urls
