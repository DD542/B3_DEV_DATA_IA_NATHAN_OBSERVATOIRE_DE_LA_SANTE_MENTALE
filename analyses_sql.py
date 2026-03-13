import pandas as pd
from sqlalchemy import create_engine
import os

engine = create_engine("mysql+mysqlconnector://root:root1234@localhost/suicide_prevention")

os.makedirs("resultats_analyses", exist_ok=True)

queries = {

    "1_deces_par_departement": """
        SELECT d.dept_nom, d.region_nom,
               ROUND(SUM(sd.nb_deces), 0) AS total_deces
        FROM suicides_deces sd
        JOIN departements d ON sd.dept_code = d.dept_code
        GROUP BY d.dept_nom, d.region_nom
        ORDER BY total_deces DESC
    """,

    "2_taux_par_region": """
        SELECT d.region_nom,
               ROUND(AVG(sd.taux_brut), 2) AS taux_moyen,
               COUNT(DISTINCT d.dept_code) AS nb_departements
        FROM suicides_deces sd
        JOIN departements d ON sd.dept_code = d.dept_code
        GROUP BY d.region_nom
        ORDER BY taux_moyen DESC
    """,

    "3_top10_departements": """
        SELECT d.dept_nom, d.region_nom,
               ROUND(AVG(sd.taux_brut), 2) AS taux_moyen
        FROM suicides_deces sd
        JOIN departements d ON sd.dept_code = d.dept_code
        GROUP BY d.dept_nom, d.region_nom
        ORDER BY taux_moyen DESC
        LIMIT 10
    """,

    "4_evolution_annuelle": """
        SELECT annee,
               ROUND(AVG(taux_brut), 2) AS taux_moyen_deces,
               ROUND(SUM(nb_deces), 0)  AS total_deces
        FROM suicides_deces
        GROUP BY annee
        ORDER BY annee
    """,

    "5_comparaison_sexe": """
        SELECT sx.sexe,
               ROUND(AVG(sd.taux_brut), 2)    AS taux_moyen_deces,
               ROUND(AVG(u.taux_passages), 2) AS taux_moyen_urgences
        FROM dim_sexe sx
        LEFT JOIN suicides_deces sd ON sx.id_sexe = sd.id_sexe
        LEFT JOIN urgences_gestes u ON sx.id_sexe = u.id_sexe
        WHERE sx.sexe IN ('Hommes', 'Femmes')
        GROUP BY sx.sexe
    """,

    "6_comparaison_age": """
        SELECT a.classe_age,
               ROUND(AVG(sd.taux_brut), 2)       AS taux_deces_moyen,
               ROUND(AVG(u.taux_passages), 2)    AS taux_urgences_moyen,
               ROUND(AVG(h.taux_brut_hospit), 2) AS taux_hospit_moyen
        FROM dim_age a
        LEFT JOIN suicides_deces sd ON a.id_age = sd.id_age
        LEFT JOIN urgences_gestes u ON a.id_age = u.id_age
        LEFT JOIN hospit_gestes h   ON a.id_age = h.id_age
        GROUP BY a.classe_age
        ORDER BY taux_deces_moyen DESC
    """,

    "7_zones_crise_sans_psychiatres": """
        SELECT d.dept_nom, d.region_nom,
               ROUND(AVG(sd.taux_brut), 2) AS taux_suicide
        FROM suicides_deces sd
        JOIN departements d ON sd.dept_code = d.dept_code
        GROUP BY d.dept_nom, d.region_nom
        HAVING taux_suicide > 15
        ORDER BY taux_suicide DESC
    """,
}

print("📊 Exécution des analyses SQL...\n")

for nom, sql in queries.items():
    df = pd.read_sql(sql, engine)
    chemin = f"resultats_analyses/{nom}.csv"
    df.to_csv(chemin, index=False, encoding="utf-8-sig")
    print(f"✅ {nom}")
    print(df.to_string(index=False))
    print()

print("\n✅ Tous les résultats exportés dans le dossier resultats_analyses/")