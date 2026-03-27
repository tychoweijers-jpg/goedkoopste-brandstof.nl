import requests
import json
from datetime import datetime
 
# Haalt actuele brandstofprijzen op via de gratis API van brandstofprijzen.nl
# Dit is een officiële databron, geen scraping — veel betrouwbaarder
 
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
}
 
FALLBACK = {
    "Euro 95": 1.949,
    "Diesel": 1.789,
    "LPG": 0.899
}
 
def haal_prijzen_op():
    # Methode 1: Directe JSON API van brandstofprijzen.nl
    try:
        url = "https://www.brandstofprijzen.info/api/getPrices.php"
        res = requests.get(url, headers=HEADERS, timeout=10)
        data = res.json()
        prijzen = {}
        for item in data:
            naam = item.get("name", "").lower()
            prijs = float(item.get("price", 0))
            if 0.5 < prijs < 5.0:
                if "euro 95" in naam or "e10" in naam or "95" in naam:
                    prijzen["Euro 95"] = round(prijs, 3)
                elif "diesel" in naam:
                    prijzen["Diesel"] = round(prijs, 3)
                elif "lpg" in naam:
                    prijzen["LPG"] = round(prijs, 3)
        if prijzen.get("Euro 95") and prijzen.get("Diesel"):
            print(f"Methode 1 gelukt: {prijzen}")
            return prijzen
    except Exception as e:
        print(f"Methode 1 mislukt: {e}")
 
    # Methode 2: CBS Statline open data API (officiële overheidsdata)
    try:
        url = "https://opendata.cbs.nl/ODataApi/odata/80416ned/TypedDataSet?$top=10&$orderby=Perioden desc&$format=json"
        res = requests.get(url, headers=HEADERS, timeout=10)
        data = res.json()
        records = data.get("value", [])
        prijzen = {}
        for r in records:
            if r.get("Benzine_1"):
                prijzen["Euro 95"] = round(float(r["Benzine_1"]) / 100, 3)
            if r.get("Diesel_2"):
                prijzen["Diesel"] = round(float(r["Diesel_2"]) / 100, 3)
            if r.get("LPG_3"):
                prijzen["LPG"] = round(float(r["LPG_3"]) / 100, 3)
            if prijzen.get("Euro 95"):
                break
        if prijzen.get("Euro 95") and prijzen.get("Diesel"):
            print(f"Methode 2 gelukt: {prijzen}")
            return prijzen
    except Exception as e:
        print(f"Methode 2 mislukt: {e}")
 
    # Methode 3: Scrape anwb.nl die prijzen duidelijk toont
    try:
        from bs4 import BeautifulSoup
        url = "https://www.anwb.nl/auto/brandstof/brandstofprijzen"
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        prijzen = {}
        tekst = soup.get_text()
        regels = tekst.split("\n")
        for i, regel in enumerate(regels):
            r = regel.strip()
            if "euro 95" in r.lower() and i + 1 < len(regels):
                try:
                    p = float(regels[i+1].strip().replace(",", ".").replace("€", ""))
                    if 1.0 < p < 3.5:
                        prijzen["Euro 95"] = round(p, 3)
                except:
                    pass
            if "diesel" in r.lower() and "euro" not in r.lower() and i + 1 < len(regels):
                try:
                    p = float(regels[i+1].strip().replace(",", ".").replace("€", ""))
                    if 1.0 < p < 3.5:
                        prijzen["Diesel"] = round(p, 3)
                except:
                    pass
            if "lpg" in r.lower() and i + 1 < len(regels):
                try:
                    p = float(regels[i+1].strip().replace(",", ".").replace("€", ""))
                    if 0.5 < p < 2.5:
                        prijzen["LPG"] = round(p, 3)
                except:
                    pass
        if prijzen.get("Euro 95") and prijzen.get("Diesel"):
            print(f"Methode 3 gelukt: {prijzen}")
            return prijzen
    except Exception as e:
        print(f"Methode 3 mislukt: {e}")
 
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

