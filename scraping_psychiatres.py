import requests
import pandas as pd
import time

print("🔍 Récupération des psychiatres via OpenStreetMap...")

url = "https://overpass-api.de/api/interpreter"

query = """
[out:json][timeout:60];
area["ISO3166-1"="FR"][admin_level=2]->.france;
(
  node["healthcare"="psychiatrist"](area.france);
  node["amenity"="doctors"]["healthcare:speciality"="psychiatry"](area.france);
);
out body;
"""

try:
    response = requests.post(url, data={"data": query}, timeout=60)
    print(f"  Statut : {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        elements = data.get("elements", [])
        print(f"  {len(elements)} psychiatres trouvés")

        resultats = []
        for e in elements:
            tags = e.get("tags", {})
            resultats.append({
                "nom":         tags.get("name", "Psychiatre"),
                "ville":       tags.get("addr:city", ""),
                "code_postal": tags.get("addr:postcode", ""),
                "dept_code":   tags.get("addr:postcode", "")[:2] if tags.get("addr:postcode") else "",
                "latitude":    e.get("lat", None),
                "longitude":   e.get("lon", None),
            })

        df = pd.DataFrame(resultats)
        df.to_csv("psychiatres_france.csv", index=False, encoding="utf-8-sig")
        print(f"\n✅ {len(df)} psychiatres sauvegardés dans psychiatres_france.csv")
        print(df.head(10))

    else:
        print(f"  ❌ Erreur : {response.text[:200]}")

except Exception as e:
    print(f"  ❌ Erreur : {e}")