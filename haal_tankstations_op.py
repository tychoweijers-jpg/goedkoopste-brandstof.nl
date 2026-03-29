import requests
import json
import os
import time
 
BESTAND = "tankstations.json"
MAX_OUD = 7 * 24 * 3600  # 7 dagen
 
if os.path.exists(BESTAND) and (time.time() - os.path.getmtime(BESTAND)) < MAX_OUD:
    print("Tankstations zijn recent, overslaan")
    exit()
 
print("Tankstations ophalen via OpenStreetMap...")
 
MERK_MAP = {
    "shell": "Shell", "bp": "BP", "esso": "Esso", "tango": "Tango",
    "tinq": "Tinq", "tamoil": "Tamoil", "gulf": "Gulf", "avia": "Avia",
    "texaco": "Texaco", "total": "Total", "q8": "Q8", "omo": "Omo",
    "calpam": "Calpam", "argos": "Argos",
}
 
query = """
[out:json][timeout:60];
area["ISO3166-1"="NL"]->.nl;
node["amenity"="fuel"](area.nl);
out body;
"""
 
res = requests.post("https://overpass-api.de/api/interpreter", data={"data": query}, timeout=90)
elements = res.json().get("elements", [])
print(str(len(elements)) + " tankstations gevonden")
 
stations = []
for el in elements:
    tags = el.get("tags", {})
    lat = el.get("lat")
    lon = el.get("lon")
    if not lat or not lon:
        continue
    naam_raw = (tags.get("brand") or tags.get("name") or tags.get("operator") or "Onbekend").strip()
    naam_lower = naam_raw.lower()
    merk = "Onbekend"
    for key, val in MERK_MAP.items():
        if key in naam_lower:
            merk = val
            break
    straat = tags.get("addr:street", "")
    huisnr = tags.get("addr:housenumber", "")
    stad = tags.get("addr:city", tags.get("addr:place", ""))
    adres = (straat + " " + huisnr).strip() if straat else naam_raw
    stations.append({
        "naam": naam_raw,
        "merk": merk,
        "adres": adres,
        "stad": stad,
        "postcode": tags.get("addr:postcode", ""),
        "lat": lat,
        "lon": lon,
    })
 
with open(BESTAND, "w", encoding="utf-8") as f:
    json.dump(stations, f, ensure_ascii=False)
 
print(str(len(stations)) + " tankstations opgeslagen in " + BESTAND)
