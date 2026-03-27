import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

URL = "https://www.brandstof-zoeker.nl/"  # 🔥 bron

def haal_prijzen():
    res = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(res.text, "html.parser")

    stations = []

    rows = soup.select("table tr")

    for row in rows:
        cols = row.find_all("td")

        if len(cols) < 4:
            continue

        try:
            naam = cols[0].text.strip()
            locatie = cols[1].text.strip()
            prijs = cols[2].text.strip().replace(",", ".")

            prijs = float(prijs)

            stations.append({
                "naam": naam,
                "locatie": locatie,
                "prijs": prijs
            })

        except:
            continue

    return stations


def sla_op(data):
    with open("stations.json", "w") as f:
        json.dump({
            "updated": datetime.now().isoformat(),
            "stations": data
        }, f, indent=2)


if __name__ == "__main__":
    print("⛽ ophalen...")
    data = haal_prijzen()
    print(f"gevonden: {len(data)} stations")

    sla_op(data)
    print("💾 opgeslagen")
