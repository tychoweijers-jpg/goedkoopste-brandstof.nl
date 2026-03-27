import requests
import json
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

FALLBACK = {
    "Euro 95": 1.949,
    "Diesel": 1.789,
    "LPG": 0.899
}

def haal_prijzen_op():
    try:
        url = "https://opendata.cbs.nl/ODataApi/odata/80416ned/TypedDataSet?$orderby=Perioden desc&$top=10&$format=json"
        res = requests.get(url, headers=HEADERS, timeout=15)

        if res.status_code != 200:
            print("API status fout:", res.status_code)
            return FALLBACK

        data = res.json()
        records = data.get("value", [])

        print(f"Aantal records: {len(records)}")

        for r in records:
            # 🔍 Pak juiste velden (flexibel)
            e95 = r.get("BenzineEuro95_1") or r.get("BenzineEuro95")
            diesel = r.get("Diesel_2") or r.get("Diesel")
            lpg = r.get("Lpg_3") or r.get("Lpg")

            # Skip als leeg
            if not e95 or not diesel:
                continue

            prijzen = {
                "Euro 95": round(float(e95) / 100, 3),
                "Diesel":  round(float(diesel) / 100, 3),
                "LPG":     round(float(lpg) / 100, 3) if lpg else 0.899
            }

            # Check realistische waarden
            if 1.0 < prijzen["Euro 95"] < 3.5:
                print("CBS API gelukt:", prijzen)
                return prijzen

        print("Geen bruikbare data gevonden")

    except Exception as e:
        print("CBS API mislukt:", e)

    print("Gebruik fallback prijzen")
    return FALLBACK


def sla_op(prijzen):
    data = {
        "bijgewerkt": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "prijzen": prijzen
    }

    with open("prijzen.json", "w") as f:
        json.dump(data, f, indent=2)

    print("Opgeslagen:", data)


if __name__ == "__main__":
    prijzen = haal_prijzen_op()
    sla_op(prijzen)
