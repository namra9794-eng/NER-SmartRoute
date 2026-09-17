"""
Risk-weighted route optimization over the Road graph (spec point c).

Roads form a graph: each Road is an edge between its (start_lat, start_lon)
and (end_lat, end_lon) nodes. We snap the requested source/destination to
the nearest graph nodes, then run Dijkstra twice:

  1. "fastest" cost = base_travel_time_minutes                (ignores risk)
  2. "safest"  cost = base_travel_time_minutes * risk_multiplier,
                      and BLOCKED roads are excluded entirely

Returning both lets the frontend show the classic "fastest vs. safest,
here's the delay" comparison called for in the spec.
"""
import heapq
import math
from collections import defaultdict

from roads.models import Road

RISK_MULTIPLIER = {
    "low": 1.0,
    "medium": 1.5,
    "high": 2.5,
    "critical": 5.0,
}


def _node_key(lat, lon, precision=4):
    return (round(lat, precision), round(lon, precision))


def _haversine_km(a, b):
    lat1, lon1 = a
    lat2, lon2 = b
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


class RouteGraph:
    def __init__(self, roads=None):
        self.roads = list(roads if roads is not None else Road.objects.select_related("district").all())
        self.adjacency = defaultdict(list)  # node -> [(neighbour_node, road)]
        self._build()

    def _build(self):
        for road in self.roads:
            a = _node_key(road.start_latitude, road.start_longitude)
            b = _node_key(road.end_latitude, road.end_longitude)
            self.adjacency[a].append((b, road))
            self.adjacency[b].append((a, road))  # roads are bidirectional

    def _nearest_node(self, lat, lon):
        if not self.adjacency:
            return None
        return min(self.adjacency.keys(), key=lambda n: _haversine_km(n, (lat, lon)))

    def shortest_path(self, src_lat, src_lon, dst_lat, dst_lon, avoid_risk=False):
        """Dijkstra. If avoid_risk, blocked edges are excluded and risky
        edges cost more (risk-aware / 'safest' route); otherwise plain
        travel-time shortest path ('fastest' route)."""
        start = self._nearest_node(src_lat, src_lon)
        goal = self._nearest_node(dst_lat, dst_lon)
        if start is None or goal is None:
            return None

        dist = {start: 0.0}
        prev = {}
        used_roads = {}
        visited = set()
        pq = [(0.0, start)]

        while pq:
            d, node = heapq.heappop(pq)
            if node in visited:
                continue
            visited.add(node)
            if node == goal:
                break

            for neighbour, road in self.adjacency[node]:
                if avoid_risk and road.status == Road.Status.BLOCKED:
                    continue
                cost = road.base_travel_time_minutes
                if avoid_risk:
                    cost *= RISK_MULTIPLIER.get(road.risk_level, 1.0)
                new_dist = d + cost
                if new_dist < dist.get(neighbour, float("inf")):
                    dist[neighbour] = new_dist
                    prev[neighbour] = node
                    used_roads[neighbour] = road
                    heapq.heappush(pq, (new_dist, neighbour))

        if goal not in dist:
            return None  # no traversable path

        # reconstruct
        path_roads = []
        node = goal
        while node != start:
            path_roads.append(used_roads[node])
            node = prev[node]
        path_roads.reverse()

        total_distance_km = sum(r.length_km for r in path_roads)
        total_time_minutes = dist[goal]
        max_risk = max((r.risk_level for r in path_roads), key=lambda r: RISK_MULTIPLIER.get(r, 1.0), default="low")

        return {
            "roads": path_roads,
            "distance_km": round(total_distance_km, 2),
            "estimated_travel_time_minutes": round(total_time_minutes, 1),
            "max_risk_level": max_risk,
            "passes_through_blocked_road": any(r.status == Road.Status.BLOCKED for r in path_roads),
        }
