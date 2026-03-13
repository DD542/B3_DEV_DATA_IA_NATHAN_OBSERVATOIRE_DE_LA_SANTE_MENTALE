import requests
import pandas as pd

print("🔍 Consommation API - Indicateurs sociaux par département...")

# API geo.api.gouv.fr - données officielles des départements
url = "https://geo.api.gouv.fr/departements?fields=code,nom,codeRegion&format=json"

headers = {"User-Agent": "Mozilla/5.0"}

try:
    response = requests.get(url, headers=headers, timeout=15)
    print(f"  Statut : {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"  {len(data)} départements récupérés")

        resultats = []
        for d in data:
            resultats.append({
                "dept_code":   d.get("code", ""),
                "dept_nom":    d.get("nom", ""),
                "region_code": d.get("codeRegion", ""),
            })

        df = pd.DataFrame(resultats)

        # Enrichir avec population via API
        print("\n🔍 Récupération population par département...")
        populations = []

        for _, row in df.iterrows():
            url_pop = f"https://geo.api.gouv.fr/departements/{row['dept_code']}/communes?fields=population&format=json"
            try:
                r = requests.get(url_pop, headers=headers, timeout=10)
                if r.status_code == 200:
                    communes = r.json()
                    pop_total = sum(c.get("population", 0) for c in communes if c.get("population"))
                    populations.append(pop_total)
                    print(f"  ✅ {row['dept_nom']} → {pop_total:,} habitants")
                else:
                    populations.append(None)
            except:
                populations.append(None)

        df["population"] = populations

        # Sauvegarde
        df.to_csv("donnees_departements_api.csv", index=False, encoding="utf-8-sig")
        print(f"\n✅ {len(df)} départements sauvegardés dans donnees_departements_api.csv")
        print(df.head(10))

except Exception as e:
    print(f"  ❌ Erreur : {e}")