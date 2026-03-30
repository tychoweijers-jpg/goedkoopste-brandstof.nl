import express from "express";
import fetch from "node-fetch";
import cors from "cors";

const app = express();
app.use(cors());

const PORT = process.env.PORT || 3000;

let cache = null;
let lastFetch = 0;

app.get("/api/tankstations", async (req, res) => {
  const { lat, lon, straal, fuel } = req.query;

  try {
    if (Date.now() - lastFetch < 60000 && cache) {
      return res.json(cache);
    }

    const lat1 = lat - straal / 111;
    const lat2 = lat + straal / 111;
    const lon1 = lon - straal / (111 * Math.cos(lat * Math.PI / 180));
    const lon2 = lon + straal / (111 * Math.cos(lat * Math.PI / 180));

    const fuelMap = {
      Euro95: "EURO95",
      Diesel: "DIESEL",
      LPG: "LPG"
    };

    const url = `https://api.anwb.nl/routing/points-of-interest/v3/all?type-filter=FUEL_STATION&bounding-box-filter=${lat1},${lon1},${lat2},${lon2}&fuel-types-filter=${fuelMap[fuel]}`;

    const response = await fetch(url, {
      headers: {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0"
      }
    });

    const data = await response.json();

    const mapped = (data.pointsOfInterest || []).map(p => ({
      name: p.name,
      latitude: p.location?.latitude,
      longitude: p.location?.longitude,
      street: p.address?.street,
      house_number: p.address?.houseNumber,
      city: p.address?.city,
      price: p.fuels?.[0]?.price
    }));

    const result = { locations: mapped };

    cache = result;
    lastFetch = Date.now();

    res.json(result);

  } catch (err) {
    res.status(500).json({ error: "API error" });
  }
});

app.listen(PORT, () => {
  console.log("Server draait op poort " + PORT);
});
