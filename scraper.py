def haal_prijzen_op():
    try:
        url = "https://opendata.cbs.nl/ODataApi/odata/80416ned/TypedDataSet?$top=5&$format=json"
        res = requests.get(url, headers=HEADERS, timeout=15)
        data = res.json()

        # Probeer beide structuren
        records = data.get("value") or data.get("d", {}).get("results", [])

        print(f"Aantal records: {len(records)}")

        for r in records:
            print("Record keys:", r.keys())  # 🔍 DEBUG

            e95 = r.get("BenzineEuro95_1") or r.get("BenzineEuro95")
            diesel = r.get("Diesel_2") or r.get("Diesel")
            lpg = r.get("Lpg_3") or r.get("Lpg")

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
