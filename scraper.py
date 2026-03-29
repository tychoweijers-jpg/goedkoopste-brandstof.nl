import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
 
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
}
 
def vind_prijs(tekst, min_p=1.0, max_p=3.5):
    matches = re.findall(r'\b(\d)[,\.](\d{3})\b', tekst)
    for m in matches:
        p = float(m[0] + "." + m[1])
        if min_p < p < max_p:
            return p
    matches = re.findall(r'\b(\d)[,\.](\d{2})\b', tekst)
    for m in matches:
        p = float(m[0] + "." + m[1])
        if min_p < p < max_p:
            return p
    return None
 
def scrape_unitedconsumers():
    try:
        url = "https://www.unitedconsumers.com/tanken/brandstofprijzen"
        res = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")
        tekst = soup.get_text(" ")
        e95 = diesel = lpg = None
        for regel in tekst.split("\n"):
            r = regel.lower()
            if ("euro 95" in r or "e10" in r) and not e95:
                p = vind_prijs(regel)
                if p: e95 = p
            if "diesel" in r and "premium" not in r and not diesel:
                p = vind_prijs(regel)
                if p: diesel = p
            if "lpg" in r and not lpg:
                p = vind_prijs(regel, 0.5, 2.5)
                if p: lpg = p
        if e95 and diesel:
            print(f"UnitedConsumers gelukt: E95={e95}, Diesel={diesel}")
            return {"Euro 95": e95, "Diesel": diesel, "LPG": lpg or 0.899}
    except Exception as e:
        print(f"UnitedConsumers mislukt: {e}")
    return None
 
def scrape_anwb():
    try:
        url = "https://www.anwb.nl/auto/brandstof/brandstofprijzen"
        res = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")
        tekst = soup.get_text(" ")
        e95 = diesel = lpg = None
        for regel in tekst.split("\n"):
            r = regel.lower()
            if ("euro 95" in r or "benzine" in r) and not e95:
                p = vind_prijs(regel)
                if p: e95 = p
            if "diesel" in r and "premium" not in r and not diesel:
                p = vind_prijs(regel)
                if p: diesel = p
            if "lpg" in r and not lpg:
                p = vind_prijs(regel, 0.5, 2.5)
                if p: lpg = p
        if e95 and diesel:
            print(f"ANWB gelukt: E95={e95}, Diesel={diesel}")
            return {"Euro 95": e95, "Diesel": diesel, "LPG": lpg or 0.899}
    except Exception as e:
        print(f"ANWB mislukt: {e}")
    return None
 
def scrape_tango():
    try:
        url = "https://www.tango.nl/tanken/brandstofprijzen/"
        res = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")
        tekst = soup.get_text(" ")
        e95 = diesel = None
        for regel in tekst.split("\n"):
            r = regel.lower()
            if ("euro 95" in r or "e10" in r) and not e95:
                p = vind_prijs(regel)
                if p: e95 = p
            if "diesel" in r and "premium" not in r and not diesel:
                p = vind_prijs(regel)
                if p: diesel = p
        if e95 and diesel:
            print(f"Tango gelukt: E95={e95}, Diesel={diesel}")
            return {"Euro 95": e95, "Diesel": diesel, "LPG": 0.899}
    except Exception as e:
        print(f"Tango mislukt: {e}")
    return None
 
def haal_prijzen_op():
    basis = None
    for fn in [scrape_unitedconsumers, scrape_anwb, scrape_tango]:
        basis = fn()
        if basis:
            break
 
    if not basis:
        print("Alle methodes mislukt, gebruik fallback")
        basis = {"Euro 95": 1.949, "Diesel": 1.789, "LPG": 0.899}
 
    # Merkprijzen berekend op basis van bekende prijsverschillen
    offsets = {
        "Tango":  {"e95": -0.14, "diesel": -0.12},
        "Tinq":   {"e95": -0.09, "diesel": -0.08},
        "Avia":   {"e95": -0.06, "diesel": -0.05},
        "Tamoil": {"e95": -0.05, "diesel": -0.04},
        "Gulf":   {"e95": -0.03, "diesel": -0.02},
        "BP":     {"e95":  0.02, "diesel":  0.02},
        "Esso":   {"e95":  0.03, "diesel":  0.03},
        "Shell":  {"e95":  0.05, "diesel":  0.04},
    }
 
    merkprijzen = {}
    for merk, off in offsets.items():
        merkprijzen[merk] = {
            "Euro 95": round(basis["Euro 95"] + off["e95"], 3),
            "Diesel":  round(basis["Diesel"] + off["diesel"], 3),
            "LPG":     basis.get("LPG", 0.899)
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
    print(f"Klaar: {output['bijgewerkt']} — basis: {data['basis']}")
 
if __name__ == "__main__":
    data = haal_prijzen_op()
    sla_op(data
