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
    try:
        url = "https://opendata.cbs.nl/ODataApi/odata/80416ned/TypedDataSet?$top=5&$format=json"
        res = requests.get(url, headers=HEADERS, timeout=15)
        records = res.json().get("value", [])
        for r in records:
            e95 = r.get("BenzineEuro95_1")
            diesel = r.get("Diesel_2")
            lpg = r.get("Lpg_3")
            if e95 and diesel:
                prijzen = {
                    "Euro 95": round(float(e95) / 100, 3),
                    "Diesel":  round(float(diesel) / 100, 3),
                    "LPG":     round(float(lpg) / 100, 3) if lpg else 0.899
                }
                if 1.0 < prijzen["Euro 95"] < 3.5:
                    print(f"CBS API gelukt: {prijzen}")
                    return prijzen
        print("CBS records leeg of prijzen buiten bereik")
    except Exception as e:
        print(f"CBS API mislukt: {e}")
 
    print("Gebruik fallback prijzen")
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
 
