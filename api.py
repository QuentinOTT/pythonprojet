"""api.py — Téléchargement des données REST Countries."""
import requests

API_URL = "https://restcountries.com/v3.1/all?fields=name,region,population,area"
TIMEOUT = 15

def download_countries():
    """Retourne une liste de tuples (name, region, population, area)."""
    resp = requests.get(API_URL, timeout=TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    rows = []
    for c in data:
        name       = c.get("name", {}).get("common", "Unknown")
        region     = c.get("region", "Unknown") or "Unknown"
        population = int(c.get("population", 0))
        area       = float(c.get("area") or 0.0)
        rows.append((name, region, population, area))
    return rows