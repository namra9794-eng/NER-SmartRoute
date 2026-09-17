from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .models import Alert
from .serializers import AlertSerializer


class AlertViewSet(viewsets.ModelViewSet):
    """
    GET /api/alerts/?active=true&severity=critical
    GET /api/alerts/?lang=as   -> (client resolves translation client-side
                                    from the `translations` array)
    """
    queryset = Alert.objects.select_related("district", "road").prefetch_related("translations").all()
    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["alert_type", "severity", "active", "district", "road"]
