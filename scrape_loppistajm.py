# Skapad: 2025-07-29 21:44

#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import uuid

BASE_URL = "https://loppistajm.se/kalender.html"
EVENT_URL_PREFIX = "https://loppistajm.se/"

PLACE_COORDINATES = {
    "Hötorget": (59.3358, 18.0636),
    "Karlaplan": (59.3394, 18.0966),
    "Solvalla": (59.3700, 17.9383),
    "Täby Arninge": (59.4502, 18.0705),
    "Fatbursparken": (59.3140, 18.0615),
    "Hågelby": (59.2397, 17.8445),
    "Roslagsstoppet": (59.5142, 18.3057),
    "Sickla": (59.3067, 18.1213),
    "Liljeholmen": (59.3108, 18.0213),
    "Värtahamnen": (59.3483, 18.1090),
    "Viksjö": (59.4210, 17.8030),
    "Bro Centrum": (59.5150, 17.6370),
    "Edsberg": (59.4451, 17.9865),
    "Huvudsta": (59.3565, 17.9903),
    "Kista": (59.4021, 17.9447),
    "Vällingby": (59.3639, 17.8722),
    "Vällingby C": (59.3622, 17.8724),
    "Åregaraget": (59.3610, 17.8721),
}

def parse_event(text, href):
    try:
        parts = text.strip().split(" ", 2)
        if len(parts) < 2:
            return None

        date_raw = parts[0]
        title = parts[1] + (" " + parts[2] if len(parts) > 2 else "")
        day, month = map(int, date_raw.split("/"))
        year = datetime.now().year
        dt = datetime(year, month, day, 10, 0)

        # Matcha plats från titeln
        matched_latlon = (59.33, 18.06)
        for name, coords in PLACE_COORDINATES.items():
            if name.lower() in title.lower():
                matched_latlon = coords
                break

        return {
            "id": "loppistajm-" + str(uuid.uuid4())[:8],
            "title": title.strip(" >"),
            "description": "Hämtad från loppistajm.se",
            "startTime": dt.isoformat(),
            "endTime": dt.replace(hour=15).isoformat(),
            "location": {
                "address": title.split()[-1],
                "city": "Stockholm",
                "district": "",
                "latitude": matched_latlon[0],
                "longitude": matched_latlon[1]
            },
            "url": EVENT_URL_PREFIX + href.strip("../"),
            "organizer": "Loppistajm",
            "tags": ["scraped"]
        }
    except Exception as e:
        print("⚠️ Hoppar event:", text, e)
        return None

def scrape():
    print(f"🔍 Hämtar {BASE_URL}")
    resp = requests.get(BASE_URL)
    soup = BeautifulSoup(resp.content, "html.parser")

    events = []
    for li in soup.select("li"):
        a = li.find("a")
        if not a or not a.text.strip():
            continue
        event = parse_event(a.text, a.get("href", ""))
        if event:
            events.append(event)

    print(f"✅ Hittade {len(events)} event")
    with open("loppisar.json", "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    print("📁 Skrev till loppisar.json")

if __name__ == "__main__":
    scrape()