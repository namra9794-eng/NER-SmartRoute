from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user supporting the platform's role-based access:
    - ADMIN: MDoNER / state nodal officers, full access
    - FIELD_OFFICIAL: uploads geo-tagged incident reports from remote locations
    - LOGISTICS_OPERATOR: manages vehicles & shipments
    - VIEWER: read-only dashboard access (e.g. district authorities)
    """

    class Role(models.TextChoices):
        ADMIN = "admin", "Administrator"
        FIELD_OFFICIAL = "field_official", "Field Official"
        LOGISTICS_OPERATOR = "logistics_operator", "Logistics Operator"
        VIEWER = "viewer", "Viewer"

    role = models.CharField(max_length=30, choices=Role.choices, default=Role.VIEWER)
    phone_number = models.CharField(max_length=20, blank=True)
    district = models.CharField(max_length=100, blank=True, help_text="Home district / area of operation")
    preferred_language = models.CharField(max_length=10, default="en")

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
