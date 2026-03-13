from flask import Flask, jsonify
from sqlalchemy import create_engine, text
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

engine = create_engine("mysql+mysqlconnector://root:root1234@localhost/suicide_prevention")

# ── 1. Liste tous les départements ───────────────────────
@app.route("/api/departements", methods=["GET"])
def get_departements():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT dept_code, dept_nom, region_nom FROM departements"))
        data = [dict(row._mapping) for row in result]
    return jsonify(data)

# ── 2. Taux de suicide par département ───────────────────
@app.route("/api/deces", methods=["GET"])
def get_deces():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT d.dept_code, d.dept_nom, d.region_nom,
                   ROUND(AVG(sd.taux_brut), 2) AS taux_moyen,
                   ROUND(SUM(sd.nb_deces), 0)  AS total_deces
            FROM suicides_deces sd
            JOIN departements d ON sd.dept_code = d.dept_code
            GROUP BY d.dept_code, d.dept_nom, d.region_nom
            ORDER BY taux_moyen DESC
        """))
        data = [dict(row._mapping) for row in result]
    return jsonify(data)

# ── 3. Top 10 départements ────────────────────────────────
@app.route("/api/top10", methods=["GET"])
def get_top10():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT d.dept_nom, d.region_nom,
                   ROUND(AVG(sd.taux_brut), 2) AS taux_moyen
            FROM suicides_deces sd
            JOIN departements d ON sd.dept_code = d.dept_code
            GROUP BY d.dept_nom, d.region_nom
            ORDER BY taux_moyen DESC
            LIMIT 10
        """))
        data = [dict(row._mapping) for row in result]
    return jsonify(data)

# ── 4. Évolution annuelle ─────────────────────────────────
@app.route("/api/evolution", methods=["GET"])
def get_evolution():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT annee,
                   ROUND(AVG(taux_brut), 2) AS taux_moyen,
                   ROUND(SUM(nb_deces), 0)  AS total_deces
            FROM suicides_deces
            GROUP BY annee ORDER BY annee
        """))
        data = [dict(row._mapping) for row in result]
    return jsonify(data)

# ── 5. Stats par région ───────────────────────────────────
@app.route("/api/region/<nom>", methods=["GET"])
def get_region(nom):
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT d.dept_nom,
                   ROUND(AVG(sd.taux_brut), 2) AS taux_moyen,
                   ROUND(SUM(sd.nb_deces), 0)  AS total_deces
            FROM suicides_deces sd
            JOIN departements d ON sd.dept_code = d.dept_code
            WHERE d.region_nom = :nom
            GROUP BY d.dept_nom
            ORDER BY taux_moyen DESC
        """), {"nom": nom})
        data = [dict(row._mapping) for row in result]
    return jsonify(data)

# ── 6. Liste des psychiatres ──────────────────────────────
@app.route("/api/psychiatres", methods=["GET"])
def get_psychiatres():
    import pandas as pd
    df = pd.read_csv("psychiatres_france.csv")
    df = df.dropna(subset=["latitude", "longitude"])
    return jsonify(df.to_dict(orient="records"))

# ── Lancement ─────────────────────────────────────────────
if __name__ == "__main__":
    print("🚀 API lancée sur http://localhost:5000")
    print("📌 Endpoints disponibles :")
    print("   http://localhost:5000/api/departements")
    print("   http://localhost:5000/api/deces")
    print("   http://localhost:5000/api/top10")
    print("   http://localhost:5000/api/evolution")
    print("   http://localhost:5000/api/region/Bretagne")
    print("   http://localhost:5000/api/psychiatres")
    app.run(debug=True, port=5000)