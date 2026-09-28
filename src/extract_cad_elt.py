import json
import requests
from pathlib import Path
from datetime import datetime, timezone

API_URL = "https://ssd-api.jpl.nasa.gov/cad.api"
TIMEOUT_SECONDS = 30

HEADERS = {
    "User-Agent": "cad-elt-practice/0.1"
}

PARAMS = {
    "date-min": "2026-09-01",
    "date-max": "2026-12-31",
    "dist-max": "0.05",
    "nea": "true",
    "fullname": "true",
    "diameter": "true",
}

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw" / "cad"

def extract():
    print(f"API: {API_URL}")
    print(f"Parameters: {PARAMS}")

    response = requests.get(API_URL, params=PARAMS, headers=HEADERS, timeout=TIMEOUT_SECONDS)

    print(f"Status: {response.status_code}")
    print(f"final_URL: {response.url}")

    response.raise_for_status()

    payload = response.json()
    return payload

def save_raw(payload):
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = RAW_DIR / f"cad_{stamp}.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path

if __name__ == "__main__":
    data = extract()
    saved = save_raw(data)
    print(f"saved raw data: {saved}")






    