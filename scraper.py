import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

# Scrapet prijzen van unitedconsumers.nl
# Pas deze URL aan als de site verandert

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
}

# Handmatige fallback prijzen als scrapen mislukt
FALLBACK_PRIJZEN = {
    "Euro 95": 1.949,
    "Diesel": 1.789,
    "LPG": 0.899
}

def scrape_prijzen():
    try:
        url = "https://www.unitedconsumers.com/tanken/informatie/brandstof-prijzen.asp"
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        prijzen = {}

        # Zoek naar prijstabellen op de pagina
        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all(["td", "th"])
                if len(cells) >= 2:
                    naam = cells[0].get_text(strip=True)
                    prijs_text = cells[1].get_text(strip=True).replace(",", ".").replace("€", "").strip()
                    try:
                        prijs = float(prijs_text)
                        if 1.0 < prijs < 3.5:  # Sanity check
                            if "95" in naam or "euro" in naam.lower():
                                prijzen["Euro 95"] = prijs
                            elif "diesel" in naam.lower():
                                prijzen["Diesel"] = prijs
                            elif "lpg" in naam.lower():
                                prijzen["LPG"] = prijs
                    except ValueError:
                        continue

        if not prijzen:
            print("Scrapen mislukt, gebruik fallback prijzen")
            prijzen = FALLBACK_PRIJZEN

        return prijzen

    except Exception as e:
        print(f"Fout bij scrapen: {e}")
        return FALLBACK_PRIJZEN


def sla_op(prijzen):
    data = {
        "bijgewerkt": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "prijzen": prijzen
    }
    with open("prijzen.json", "w") as f:
        json.dump(data, f, indent=2)
    print(f"Prijzen opgeslagen: {prijzen}")


if __name__ == "__main__":
    prijzen = scrape_prijzen()
    sla_op(prijzen)
