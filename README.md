# NER Smart Logistics & Accessibility Intelligence Platform — Backend

Backend for **SIH26002** — *AI-Based Smart Logistics and Accessibility
Intelligence Platform for the North Eastern Region (NER)*
(Ministry of Development of North Eastern Region).

Built API-first with **Django + Django REST Framework**, so the web
dashboard, mobile field app, GPS simulator, and ML model all talk to one
backend. SQLite for the prototype; switch to PostgreSQL + PostGIS for
production (`USE_POSTGRES=True` in `.env`).

## How this maps to the problem statement

| Spec requirement | Implementation |
|---|---|
| a. Real-time road/bridge/transport accessibility monitoring | `roads` app — `Road`, `District` models + `/api/roads/`, `/api/districts/` |
| b. Predict disruptions (landslide/flood/rain/damage/traffic) | `ml_engine` app — `/api/predictions/risk/` |
| c. AI alternate route suggestions + delay estimates | `routes` app — risk-weighted Dijkstra, `/api/routes/optimize/` |
| d. GPS tracking of vehicles carrying essential goods | `vehicles` app — `/api/vehicles/`, `/api/vehicles/{id}/ping/` |
| e. Automated alerts (blocked roads, delays, high-risk corridors) | `alerts` app, auto-fired from `incidents`/`roads`/`vehicles` |
| f. Field officials upload geo-tagged reports/photos | `incidents` app — `/api/incidents/` (multipart photo upload) |
| g. Centralized dashboards | `dashboard` app — connectivity, bottlenecks, emergency routes, live movement |
| h. Multilingual notifications + offline sync | `AlertTranslation` model; `client_uuid`/`synced_at` on `Incident` for offline-first mobile sync |

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo_data
python manage.py runserver
```

API root: `http://127.0.0.1:8000/api/`
Admin: `http://127.0.0.1:8000/admin/`

## Auth

JWT-based. Register, then log in to get access/refresh tokens:

```bash
curl -X POST localhost:8000/api/auth/register/ -d '{"username":"field1","password":"Passw0rd!23","role":"field_official"}' -H "Content-Type: application/json"
curl -X POST localhost:8000/api/auth/login/ -d '{"username":"field1","password":"Passw0rd!23"}' -H "Content-Type: application/json"
```
Send `Authorization: Bearer <access>` on subsequent requests.

## Key endpoints

```
POST /api/auth/register/               POST /api/auth/login/            GET /api/auth/me/
GET/POST      /api/districts/          GET/POST/PATCH /api/roads/
GET/POST      /api/incidents/          (multipart: photo, latitude, longitude, incident_type, severity, occurred_at, client_uuid)
GET/POST      /api/vehicles/           POST /api/vehicles/{id}/ping/     GET /api/vehicles/{id}/history/
GET/POST      /api/logistics/shipments/
POST          /api/routes/optimize/    GET /api/routes/history/
GET/POST      /api/weather/            POST /api/weather/sync/?district_id=1
POST          /api/predictions/risk/
GET/POST      /api/alerts/
GET           /api/dashboard/connectivity/
GET           /api/dashboard/bottlenecks/
GET           /api/dashboard/emergency-routes/
GET           /api/dashboard/live-movement/
```

## Example: risk prediction

```bash
curl -X POST localhost:8000/api/predictions/risk/ \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"rainfall_mm_24h": 82, "road_condition_score": 7, "previous_incidents_count": 4, "traffic_congestion_pct": 70}'
# -> {"risk": "high", "probability": 0.87, "edge_cost_multiplier": 4.48}
```

## Example: route optimization

```bash
curl -X POST localhost:8000/api/routes/optimize/ \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"source_name":"Guwahati","destination_name":"Itanagar","source_latitude":26.1445,"source_longitude":91.7362,"destination_latitude":27.0844,"destination_longitude":93.6053}'
```
Returns both the fastest route and the risk-avoiding safest route (excluding
blocked roads, penalizing risky ones), plus the estimated delay between them.

## Build order (matches the MVP-first plan)

1. Roads + Incidents + Vehicles + REST API → map dashboard (works standalone)
2. ML risk engine → Route optimization
3. Weather integration → Alerts
4. Offline sync polish, multilingual alert translations, PostGIS migration

## Next steps for production

- Swap SQLite → PostgreSQL + PostGIS (`USE_POSTGRES=True`); replace flat
  lat/lon fields with `PointField`/`LineStringField` for true GIS queries.
- Replace `ml_engine/risk_model.py`'s rule-based scorer with a trained
  model (`trained_model.pkl`) — the request/response contract is unchanged.
- Add a push-notification/SMS gateway consuming `Alert`/`AlertTranslation`.
- Add Celery + Redis for scheduled `weather/sync` polling per district.
