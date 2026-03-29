import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
 
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "nl-NL,nl;q=0.9",
}
 
# Actuele GLA prijzen 29 maart 2026 (bron: unitedconsumers.com)
FALLBACK = {"Euro 95": 2.180, "Diesel": 2.040, "LPG": 0.979}
 
def vind_prijs(tekst, min_p=1.5, max_p=3.0):
    matches = re.findall(r'\b([12])[\.,](\d{3})\b', tekst)
    for m in matches:
        p = round(float(m[0] + "." + m[1]), 3)
        if min_p < p < max_p:
            return p
    return None
 
def scrape_unitedconsumers():
    """Scrape de GLA prijzen van UnitedConsumers"""
    try:
        url = "https://www.unitedconsumers.com/tanken/brandstofprijzen"
        res = requests.get(url, headers=HEADERS, timeout=20)
        print("UC status: " + str(res.status_code))
        soup = BeautifulSoup(res.text, "html.parser")
 
        # Zoek alle prijzen in de pagina
        tekst = soup.get_text(" ", strip=True)
        print("UC tekst fragment: " + tekst[:500])
 
        e95 = diesel = lpg = None
 
        # Zoek per regel
        for regel in tekst.replace("  ", "\n").split("\n"):
            r = regel.lower().strip()
            if len(r) < 3:
                continue
            if ("euro 95" in r or "e10" in r or "benzine" in r) and not e95:
                p = vind_prijs(regel)
                if p:
                    e95 = p
                    print("UC E95 gevonden: " + str(p) + " in: " + regel[:50])
            if "diesel" in r and "premium" not in r and "bio" not in r and not diesel:
                p = vind_prijs(regel)
                if p:
                    diesel = p
                    print("UC Diesel gevonden: " + str(p) + " in: " + regel[:50])
            if "lpg" in r and not lpg:
                p = vind_prijs(regel, 0.5, 1.5)
                if p:
                    lpg = p
 
        if e95 and diesel:
            print("UC gelukt: E95=" + str(e95) + " Diesel=" + str(diesel))
            return {"Euro 95": e95, "Diesel": diesel, "LPG": lpg or 0.979}
        print("UC mislukt: E95=" + str(e95) + " Diesel=" + str(diesel))
    except Exception as e:
        print("UC fout: " + str(e))
    return None
 
def scrape_tango():
    """Scrape Tango prijzen en bereken basis daaruit"""
    try:
        url = "https://www.tango.nl/tanken/brandstofprijzen/"
        res = requests.get(url, headers=HEADERS, timeout=20)
        print("Tango status: " + str(res.status_code))
        tekst = res.text
 
        # Vind alle prijzen
        alle = re.findall(r'\b([12])[\.,](\d{3})\b', tekst)
        uniek = []
        for m in alle:
            p = round(float(m[0] + "." + m[1]), 3)
            if 1.5 < p < 2.8 and p not in uniek:
                uniek.append(p)
        uniek.sort()
        print("Tango prijzen gevonden: " + str(uniek))
 
        if len(uniek) >= 2:
            # Tango is goedkoopste merk, voeg offset toe voor basis
            diesel_tango = uniek[0]
            e95_tango = uniek[1] if len(uniek) > 1 else uniek[0] + 0.14
            # Bereken basisprijs (Tango is gemiddeld 14ct goedkoper voor E95, 12ct voor diesel)
            e95_basis = round(e95_tango + 0.14, 3)
            diesel_basis = round(diesel_tango + 0.12, 3)
            if 1.8 < e95_basis < 2.8 and 1.7 < diesel_basis < 2.8:
                print("Tango gelukt: E95 basis=" + str(e95_basis) + " Diesel basis=" + str(diesel_basis))
                return {"Euro 95": e95_basis, "Diesel": diesel_basis, "LPG": 0.979}
    except Exception as e:
        print("Tango fout: " + str(e))
    return None
 
def haal_prijzen_op():
    basis = None
    for fn in [scrape_unitedconsumers, scrape_tango]:
        basis = fn()
        if basis:
            break
 
    if not basis:
        print("Scraping mislukt, gebruik actuele GLA van 29 maart 2026")
        basis = FALLBACK
 
    offsets = {
        "Tango":    {"Euro 95": -0.14, "Diesel": -0.12},
        "Tinq":     {"Euro 95": -0.09, "Diesel": -0.08},
        "Avia":     {"Euro 95": -0.06, "Diesel": -0.05},
        "Calpam":   {"Euro 95": -0.06, "Diesel": -0.05},
        "Argos":    {"Euro 95": -0.05, "Diesel": -0.04},
        "Tamoil":   {"Euro 95": -0.05, "Diesel": -0.04},
        "Omo":      {"Euro 95": -0.04, "Diesel": -0.03},
        "Gulf":     {"Euro 95": -0.03, "Diesel": -0.02},
        "Q8":       {"Euro 95": -0.02, "Diesel": -0.01},
        "Total":    {"Euro 95":  0.00, "Diesel":  0.00},
        "Texaco":   {"Euro 95":  0.01, "Diesel":  0.01},
        "BP":       {"Euro 95":  0.02, "Diesel":  0.02},
        "Esso":     {"Euro 95":  0.03, "Diesel":  0.03},
        "Shell":    {"Euro 95":  0.05, "Diesel":  0.04},
        "Onbekend": {"Euro 95":  0.00, "Diesel":  0.00},
    }
 
    merkprijzen = {}
    for merk, off in offsets.items():
        merkprijzen[merk] = {
            "Euro 95": round(basis["Euro 95"] + off["Euro 95"], 3),
            "Diesel":  round(basis["Diesel"] + off["Diesel"], 3),
            "LPG":     basis.get("LPG", 0.979)
        }
 
    return {"basis": basis, "merken": merkprijzen}
 
def sla_op(data):
    output = {
        "bijgewerkt": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "prijzen": data["basis"],
        "merkprijzen": data["merken"]
    }
    with open("prijzen.json", "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print("Opgeslagen: " + str(data["basis"]))
 
if __name__ == "__main__":
    data = haal_prijzen_op()
    sla_op(data)
 
