"""BACKEND: Rotonda garage logic (plain Python, no database access).

Two small pieces live here so the routes in app.py stay short:
  1. ROUTES: hand-written, fictional-or-approximate sample ride cards.
  2. service_alert(): simple arithmetic that compares a ride to the km left
     before a bike's next service. No heap, tree, or graph is needed.
"""

from urllib.parse import quote_plus

# Show a "service soon" chip when this many km (or fewer) are left.
SERVICE_SOON_KM = 300

# Distances are approximate one-way sample values for the class demo.
ROUTES = [
    {
        "slug": "buda",
        "name": "BUDA Highway to Malaybalay",
        "destination": "Malaybalay City, Bukidnon",
        "one_way_km": 140,
        "duration": "2.5 hrs one way",
        "terrain": "High elevation, sweeping twisties",
        "vibe": "Escape the heat and take on Mindanao's famous elevated highway. "
                "Crisp mountain air, fast sweepers, pine-tree views, and coffee stops.",
    },
    {
        "slug": "claveria",
        "name": "Claveria Highlands Run",
        "destination": "Claveria, Misamis Oriental",
        "one_way_km": 60,
        "duration": "1.5 hrs one way",
        "terrain": "Cool plateau, rolling curves",
        "vibe": "A shorter climb into chilly highland air with open views. "
                "Great for a half-day ride and a warm drink at the top.",
    },
    {
        "slug": "coastal",
        "name": "Sunday Coastal Cruise (sample)",
        "destination": "Seaside rest stop",
        "one_way_km": 35,
        "duration": "1 hr one way",
        "terrain": "Flat coastal road",
        "vibe": "An easy cruise to shake out the bike. Good for testing a new part "
                "or breaking in fresh oil.",
    },
]


def route_with_totals(route):
    """Add the round-trip distance and a Google Maps search link."""
    result = dict(route)
    result["round_trip_km"] = route["one_way_km"] * 2
    result["maps_url"] = ("https://www.google.com/maps/search/?api=1&query="
                          + quote_plus(route["destination"]))
    return result


def km_left(bike):
    """Kilometres until the next service. Negative means overdue."""
    return bike["service_due_km"] - bike["odometer_km"]


def service_alert(bike, ride_km):
    """Garage Intelligence: compare a ride with the km left before service.

    Returns (level, message). level is "ok", "warn", or "overdue".
    """
    left = km_left(bike)
    name = bike["title"]
    if left < 0:
        return ("overdue",
                f"{name} is {abs(left)} km past its service. "
                "Book the service before a long ride.")
    if ride_km > left:
        return ("warn",
                f"You're planning a {ride_km} km ride on your {name}! "
                f"Its service is due in {left} km. Do the service before "
                "rolling out, or schedule it right after.")
    return ("ok",
            f"{name} is ready: {left} km left before service, "
            f"and this ride is {ride_km} km.")


def service_status(item):
    """Chip data for a motorcycle card, or None if there are no readings."""
    if item.get("odometer_km") is None or item.get("service_due_km") is None:
        return None
    left = km_left(item)
    if left < 0:
        level = "overdue"
    elif left <= SERVICE_SOON_KM:
        level = "warn"
    else:
        level = "ok"
    return {"left": left, "level": level}
