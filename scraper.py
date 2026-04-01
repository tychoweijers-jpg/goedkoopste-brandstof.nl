import requests
import json
from datetime import datetime
 
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://www.anwb.nl/",
    "Origin": "https://www.anwb.nl",
}
 
# Heel Nederland in een bounding box
BBOX = "50.75,3.36,53.47,7.21"
 
def haal_alle_stations():
    brandstoffen = ["EURO95", "DIESEL", "AUTOGAS"]
    alle_stations = {}
 
    for brandstof in brandstoffen:
        url = f"https://api.anwb.nl/routing/points-of-interest/v3/all?type-filter=FUEL_STATION&bounding-box-filter={BBOX}&fuel-types-filter={brandstof}"
        try:
            res = requests.get(url, headers=HEADERS, timeout=30)
            print(f"ANWB {brandstof} status: {res.status_code}")
            if res.status_code == 200:
                data = res.json()
                stations = data.get("value", [])
                print(f"{brandstof}: {len(stations)} stations gevonden")
                for s in stations:
                    sid = s.get("id")
                    if not sid:
                        continue
                    if sid not in alle_stations:
                        alle_stations[sid] = {
                            "id": sid,
                            "naam": s.get("title", "Tankstation"),
                            "adres": s.get("address", {}).get("streetAddress", ""),
                            "stad": s.get("address", {}).get("city", ""),
                            "postcode": s.get("address", {}).get("postalCode", ""),
                            "lat": s.get("coordinates", {}).get("latitude"),
                            "lon": s.get("coordinates", {}).get("longitude"),
                            "prijzen": {}
                        }
                    for p in s.get("prices", []):
                        if p.get("value", 0) > 0:
                            alle_stations[sid]["prijzen"][p["fuelType"]] = p["value"]
            else:
                print(f"Fout bij {brandstof}: {res.status_code}")
        except Exception as e:
            print(f"Fout bij {brandstof}: {e}")
 
    return list(alle_stations.values())
 
def sla_op(stations):
    output = {
        "bijgewerkt": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "stations": stations
    }
    with open("prijzen.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False)
    print(f"Opgeslagen: {len(stations)} stations in prijzen.json")
 
if __name__ == "__main__":
    print("Stations ophalen van ANWB API...")
    stations = haal_alle_stations()
    sla_op(stations)
