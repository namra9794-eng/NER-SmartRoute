"""
Automated alert generation (spec point e). Called from incidents/roads/
routes/weather signals so every subsystem funnels into one alert feed
that the dashboard and mobile/web push-notification layer can consume.
"""
from .models import Alert


def raise_alert_for_incident(incident):
    if incident.severity not in ("high", "critical"):
        return None
    return Alert.objects.create(
        alert_type=Alert.AlertType.BLOCKED_ROAD if incident.severity == "critical" else Alert.AlertType.HIGH_RISK,
        severity=Alert.Severity.CRITICAL if incident.severity == "critical" else Alert.Severity.WARNING,
        title=f"{incident.get_incident_type_display()} reported near {incident.district_name or 'unknown district'}",
        message=incident.description or f"{incident.get_incident_type_display()} reported with {incident.severity} severity.",
        road=incident.road,
        is_auto_generated=True,
    )


def raise_alert_for_road(road):
    if road.status == road.Status.BLOCKED:
        return Alert.objects.create(
            alert_type=Alert.AlertType.BLOCKED_ROAD,
            severity=Alert.Severity.CRITICAL,
            title=f"{road.name} is blocked",
            message=f"{road.name} in {road.district.name} is currently blocked. Vehicles will be re-routed.",
            district=road.district,
            road=road,
        )
    if road.risk_level in ("high", "critical"):
        return Alert.objects.create(
            alert_type=Alert.AlertType.HIGH_RISK,
            severity=Alert.Severity.WARNING,
            title=f"{road.name} is a high-risk corridor",
            message=f"{road.name} in {road.district.name} has a {road.risk_level} disruption risk.",
            district=road.district,
            road=road,
        )
    return None


def raise_alert_for_vehicle_delay(vehicle):
    return Alert.objects.create(
        alert_type=Alert.AlertType.VEHICLE_DELAY,
        severity=Alert.Severity.WARNING,
        title=f"Vehicle {vehicle.vehicle_number} delayed",
        message=f"Vehicle {vehicle.vehicle_number} carrying {vehicle.cargo_type} is delayed en route to {vehicle.destination}.",
    )
