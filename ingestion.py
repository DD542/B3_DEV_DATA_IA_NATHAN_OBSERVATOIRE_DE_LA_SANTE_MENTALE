import mysql.connector
import pandas as pd

# Connexion à MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root1234",
    database="suicide_prevention"
)
cur = conn.cursor()

# ── Chemins vers les fichiers CSV ──────────────────────────
CSV_URGENCES = "gestes-urgences-departement-clean2.csv"
CSV_DECES    = "suicides-deces-departement-clean2.csv"
CSV_HOSPIT   = "gestes-hospit-departement-clean2.csv"

# ── Helpers pour insérer les dimensions ──────────────────
def get_or_insert_age(value):
    cur.execute("SELECT id_age FROM dim_age WHERE classe_age = %s", (value,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute("INSERT INTO dim_age (classe_age) VALUES (%s)", (value,))
    conn.commit()
    return cur.lastrowid

def get_or_insert_sexe(value):
    cur.execute("SELECT id_sexe FROM dim_sexe WHERE sexe = %s", (value,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute("INSERT INTO dim_sexe (sexe) VALUES (%s)", (value,))
    conn.commit()
    return cur.lastrowid

def clean(value):
    if pd.isna(value):
        return ""
    return str(value)

def clean_float(value):
    if pd.isna(value):
        return None
    return float(value)

# ── 1. URGENCES ───────────────────────────────────────────
print("Chargement urgences...")
df = pd.read_csv(CSV_URGENCES, encoding="utf-8-sig")
df.columns = [c.strip() for c in df.columns]

for _, r in df.iterrows():
    dept_code = str(r["Département Code"]).zfill(2)

    cur.execute("""
        INSERT IGNORE INTO departements (dept_code, dept_nom, region_code, region_nom)
        VALUES (%s, %s, %s, %s)
    """, (dept_code, clean(r["Département"]), clean(r.get("Région Code","")), clean(r.get("Région",""))))

    id_age  = get_or_insert_age(clean(r["Classe d'âge"]))
    id_sexe = get_or_insert_sexe(clean(r["Sexe"]))

    cur.execute("""
        INSERT INTO urgences_gestes (annee, dept_code, id_age, id_sexe, taux_passages)
        VALUES (%s, %s, %s, %s, %s)
    """, (int(r["Année"]), dept_code, id_age, id_sexe,
          clean_float(r["Taux de passages aux urgences pour gestes auto infligés"])))

conn.commit()
print("✅ Urgences chargées")

# ── 2. DÉCÈS ──────────────────────────────────────────────
print("Chargement décès...")
df = pd.read_csv(CSV_DECES, encoding="utf-8-sig")
df.columns = [c.strip() for c in df.columns]

for _, r in df.iterrows():
    dept_code = str(r["Département Code"]).zfill(2)

    cur.execute("""
        INSERT IGNORE INTO departements (dept_code, dept_nom)
        VALUES (%s, %s)
    """, (dept_code, clean(r["Département"])))

    id_age  = get_or_insert_age(clean(r["Classe d'âge"]))
    id_sexe = get_or_insert_sexe(clean(r["Sexe"]))

    cur.execute("""
        INSERT INTO suicides_deces (annee, dept_code, id_age, id_sexe, nb_deces, taux_brut, taux_standardise)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (int(r["Année"]), dept_code, id_age, id_sexe,
          clean_float(r["Nombre de décès"]),
          clean_float(r["Taux brut"]),
          clean_float(r["Taux standardisé"])))

conn.commit()
print("✅ Décès chargés")

# ── 3. HOSPITALISATIONS ───────────────────────────────────
print("Chargement hospitalisations...")
df = pd.read_csv(CSV_HOSPIT, encoding="utf-8-sig")
df.columns = [c.strip() for c in df.columns]

for _, r in df.iterrows():
    dept_code = str(r["Département Code"]).zfill(2)

    cur.execute("""
        INSERT IGNORE INTO departements (dept_code, dept_nom, region_nom)
        VALUES (%s, %s, %s)
    """, (dept_code, clean(r["Département"]), clean(r.get("Région",""))))

    id_age  = get_or_insert_age(clean(r["Classe d'âge"]))
    id_sexe = get_or_insert_sexe(clean(r["Sexe"]))

    cur.execute("""
        INSERT INTO hospit_gestes (annee, dept_code, id_age, id_sexe, nb_sejours, taux_brut_hospit, taux_standardise_hospit)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (int(r["Année"]), dept_code, id_age, id_sexe,
          clean_float(r["Nombre de séjours pour geste auto-infligé"]),
          clean_float(r["Taux brut d'hospitalisation pour geste auto-infligé"]),
          clean_float(r["Taux standardisé d'hospitalisation pour geste auto-infligé"])))

conn.commit()
print("✅ Hospitalisations chargées")

cur.close()
conn.close()
print("\n✅ Toutes les données sont dans MySQL !")