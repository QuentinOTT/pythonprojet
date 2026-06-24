"""api.py — Téléchargement des données REST Countries."""
import requests

API_URL = "https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/json/countries.json"
TIMEOUT = 15

def download_countries():
    """Retourne une liste de tuples (name, region, population, area)."""
    resp = requests.get(API_URL, timeout=TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    rows = []
    for c in data:
        # Support both new mirror structure and legacy REST Countries structure
        raw_name = c.get("name", "Unknown")
        if isinstance(raw_name, dict):
            name = raw_name.get("common", "Unknown")
        else:
            name = str(raw_name)
            
        region = c.get("region", "Unknown") or "Unknown"
        population = int(c.get("population") or 0)
        area = float(c.get("area_sq_km") or c.get("area") or 0.0)
        rows.append((name, region, population, area))
    return rows