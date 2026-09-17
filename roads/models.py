from django.db import models


class District(models.Model):
    """A NER district, used to roll up connectivity status for the dashboard."""
    name = models.CharField(max_length=100, unique=True)
    state = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()

    class Meta:
        ordering = ["state", "name"]

    def __str__(self):
        return f"{self.name}, {self.state}"


class Road(models.Model):
    """
    A road/bridge segment. Nodes at (start_lat, start_lon) -> (end_lat, end_lon)
    form the graph used by the routes app for shortest / lowest-risk path search.
    """

    class RoadType(models.TextChoices):
        HIGHWAY = "highway", "Highway"
        STATE_ROAD = "state_road", "State Road"
        RURAL_ROAD = "rural_road", "Rural Road"
        BRIDGE = "bridge", "Bridge"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        RISKY = "risky", "Risky"
        BLOCKED = "blocked", "Blocked"
        UNDER_REPAIR = "under_repair", "Under Repair"

    class RiskLevel(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    name = models.CharField(max_length=200)
    road_type = models.CharField(max_length=20, choices=RoadType.choices, default=RoadType.STATE_ROAD)
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name="roads")

    start_latitude = models.FloatField()
    start_longitude = models.FloatField()
    end_latitude = models.FloatField()
    end_longitude = models.FloatField()

    length_km = models.FloatField(help_text="Segment length in kilometres")
    base_travel_time_minutes = models.FloatField(help_text="Travel time under normal conditions")

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    risk_level = models.CharField(max_length=20, choices=RiskLevel.choices, default=RiskLevel.LOW)
    risk_probability = models.FloatField(default=0.0, help_text="0-1 ML-predicted disruption probability")

    landslide_prone = models.BooleanField(default=False)
    flood_prone = models.BooleanField(default=False)

    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["district", "status"])]

    def __str__(self):
        return f"{self.name} ({self.district.name})"

    @property
    def is_traversable(self):
        return self.status != self.Status.BLOCKED
