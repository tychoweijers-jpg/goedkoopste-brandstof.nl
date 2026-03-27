import requests
import json
from datetime import datetime
 
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
}
 
FALLBACK = {
    "Euro 95": 1.949,
    "Diesel": 1.789,
    "LPG": 0.899
}
 
def haal_prijzen_op():
    # Methode 1: CBS OData API — officiële overheidsdata
    try:
        url = "https://opendata.cbs.nl/ODataApi/odata/80416ned/TypedDataSet?$top=5&$format=json"
        res = requests.get(url, headers=HEADERS, timeout=15)
        records = res.json().get("value", [])
        for r in records:
            e95 = r.get("Benzine_1") or r.get("Benzine_2")
            diesel = r.get("Diesel_3") or r.get("Diesel_4") or r.get("Diesel_2")
            lpg = r.get("LPG_5") or r.get("LPG_4") or r.get("LPG_3")
            if e95 and diesel:
                prijzen = {
                    "Euro 95": round(float(e95) / 100, 3),
                    "Diesel":  round(float(diesel) / 100, 3),
                    "LPG":     round(float(lpg) / 100, 3) if lpg else 0.899
                }
                if 1.0 < prijzen["Euro 95"] < 3.5:
                    print(f"CBS API gelukt: {prijzen}")
                    return prijzen
    except Exception as e:
        print(f"CBS API mislukt: {e}")
 
    # Methode 2: Lees alle CBS veldnamen uit om juiste sleutels te vinden
    try:
        url = "https://opendata.cbs.nl/ODataApi/odata/80416ned/TypedDataSet?$top=1&$format=json"
        res = requests.get(url, headers=HEADERS, timeout=15)
        records = res.json().get("value", [])
        if records:
            r = records[0]
            print(f"CBS velden beschikbaar: {list(r.keys())}")
            prijzen = {}
            for key, val in r.items():
                if val is None:
                    continue
                try:
                    p = float(val) / 100
                except:
                    continue
                k = key.lower()
                if ("benzine" in k or "euro95" in k or "e10" in k) and 1.0 < p < 3.5:
                    prijzen["Euro 95"] = round(p, 3)
                elif "diesel" in k and 1.0 < p < 3.0:
                    prijzen["Diesel"] = round(p, 3)
                elif "lpg" in k and 0.5 < p < 2.0:
                    prijzen["LPG"] = round(p, 3)
            if prijzen.get("Euro 95") and prijzen.get("Diesel"):
                print(f"CBS methode 2 gelukt: {prijzen}")
                return prijzen
    except Exception as e:
        print(f"CBS methode 2 mislukt: {e}")
 
    # Methode 3: Tankservice.nl publieke JSON feed
    try:
        url = "https://www.tankservice.nl/api/v1/prices"
        res = requests.get(url, headers=HEADERS, timeout=10)
        data = res.json()
        prijzen = {}
        items = data if isinstance(data, list) else data.get("prices", data.get("data", []))
        for item in items:
            naam = str(item.get("name", item.get("fuel", ""))).lower()
            prijs = float(item.get("price", item.get("value", 0)))
            if 0.5 < prijs < 5.0:
                if "95" in naam or "euro" in naam:
                    prijzen["Euro 95"] = round(prijs, 3)
                elif "diesel" in naam:
                    prijzen["Diesel"] = round(prijs, 3)
                elif "lpg" in naam:
                    prijzen["LPG"] = round(prijs, 3)
        if prijzen.get("Euro 95") and prijzen.get("Diesel"):
            print(f"Tankservice gelukt: {prijzen}")
            return prijzen
    except Exception as e:
        print(f"Tankservice mislukt: {e}")
 
    print("Alle methodes mislukt, gebruik fallback")
    return FALLBACK
 
 
def sla_op(prijzen):
    data = {
        "bijgewerkt": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "prijzen": prijzen
    }
    with open("prijzen.json", "w") as f:
        json.dump(data, f, indent=2)
    print(f"Opgeslagen: {data}")
 
 
if __name__ == "__main__":
    prijzen = haal_prijzen_op()
    sla_op(prijzen)
 
