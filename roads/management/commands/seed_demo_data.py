"""
Seeds a small NER demo dataset: districts, roads, a vehicle, and a shipment,
so the API + dashboard have something to show immediately after `migrate`.

Usage: python manage.py seed_demo_data
"""
from django.core.management.base import BaseCommand

from roads.models import District, Road
from vehicles.models import Vehicle
from logistics.models import Shipment


class Command(BaseCommand):
    help = "Seed demo data for the NER logistics platform"

    def handle(self, *args, **options):
        guwahati, _ = District.objects.get_or_create(
            name="Kamrup Metropolitan", state="Assam",
            defaults={"latitude": 26.1445, "longitude": 91.7362},
        )
        tawang, _ = District.objects.get_or_create(
            name="Tawang", state="Arunachal Pradesh",
            defaults={"latitude": 27.5860, "longitude": 91.8590},
        )
        itanagar, _ = District.objects.get_or_create(
            name="Papum Pare", state="Arunachal Pradesh",
            defaults={"latitude": 27.0844, "longitude": 93.6053},
        )

        road1, _ = Road.objects.get_or_create(
            name="NH-15", district=tawang,
            defaults=dict(
                road_type=Road.RoadType.HIGHWAY,
                start_latitude=26.1445, start_longitude=91.7362,
                end_latitude=27.5860, end_longitude=91.8590,
                length_km=180, base_travel_time_minutes=240,
                status=Road.Status.RISKY, risk_level=Road.RiskLevel.HIGH,
                risk_probability=0.72, landslide_prone=True,
            ),
        )
        road2, _ = Road.objects.get_or_create(
            name="NH-13 Guwahati-Itanagar", district=itanagar,
            defaults=dict(
                road_type=Road.RoadType.HIGHWAY,
                start_latitude=26.1445, start_longitude=91.7362,
                end_latitude=27.0844, end_longitude=93.6053,
                length_km=310, base_travel_time_minutes=420,
                status=Road.Status.OPEN, risk_level=Road.RiskLevel.LOW,
                risk_probability=0.12,
            ),
        )

        vehicle, _ = Vehicle.objects.get_or_create(
            vehicle_number="NER-001",
            defaults=dict(
                cargo_type="Medicine", source="Guwahati", destination="Itanagar",
                latitude=26.20, longitude=91.90, status=Vehicle.Status.MOVING,
            ),
        )

        Shipment.objects.get_or_create(
            reference_code="SHP-0001",
            defaults=dict(
                cargo_type=Shipment.CargoType.MEDICINE,
                origin="Guwahati", destination="Itanagar",
                priority=Shipment.Priority.URGENT,
                vehicle=vehicle,
                delivery_status=Shipment.DeliveryStatus.IN_TRANSIT,
            ),
        )

        self.stdout.write(self.style.SUCCESS("Demo data seeded."))
