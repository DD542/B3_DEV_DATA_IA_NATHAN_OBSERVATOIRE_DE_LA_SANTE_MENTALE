import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import mysql.connector

# ── Connexion MySQL ───────────────────────────────────────
from sqlalchemy import create_engine
engine = create_engine("mysql+mysqlconnector://root:root1234@localhost/suicide_prevention")
conn = engine.connect()

# ── 1. ÉVOLUTION ANNUELLE ─────────────────────────────────
df_evol = pd.read_sql_query("""
    SELECT annee, ROUND(AVG(taux_brut), 2) as taux_moyen
    FROM suicides_deces
    GROUP BY annee
    ORDER BY annee
""", conn)

fig1 = px.line(
    df_evol, x="annee", y="taux_moyen",
    title="📈 Évolution du taux de suicide en France (2019-2023)",
    markers=True,
    labels={"annee": "Année", "taux_moyen": "Taux moyen (pour 100 000 hab.)"},
    color_discrete_sequence=["#E63946"]
)
fig1.update_layout(template="plotly_white")
fig1.show()

# ── 2. COMPARAISON HOMMES vs FEMMES ──────────────────────
df_sexe = pd.read_sql_query("""
    SELECT sx.sexe, ROUND(AVG(sd.taux_brut), 2) as taux_moyen
    FROM suicides_deces sd
    JOIN dim_sexe sx ON sd.id_sexe = sx.id_sexe
    WHERE sx.sexe IN ('Hommes', 'Femmes')
    GROUP BY sx.sexe
""", conn)

fig2 = px.bar(
    df_sexe, x="sexe", y="taux_moyen",
    title="👥 Taux de suicide : Hommes vs Femmes",
    labels={"sexe": "Sexe", "taux_moyen": "Taux moyen (pour 100 000 hab.)"},
    color="sexe",
    color_discrete_map={"Hommes": "#1D3557", "Femmes": "#E63946"}
)
fig2.update_layout(template="plotly_white")
fig2.show()

# ── 3. COMPARAISON PAR CLASSE D'ÂGE ──────────────────────
df_age = pd.read_sql_query("""
    SELECT a.classe_age, ROUND(AVG(sd.taux_brut), 2) as taux_moyen
    FROM suicides_deces sd
    JOIN dim_age a ON sd.id_age = a.id_age
    GROUP BY a.classe_age
    ORDER BY taux_moyen DESC
""", conn)

fig3 = px.bar(
    df_age, x="classe_age", y="taux_moyen",
    title="🎂 Taux de suicide par classe d'âge",
    labels={"classe_age": "Classe d'âge", "taux_moyen": "Taux moyen (pour 100 000 hab.)"},
    color="taux_moyen",
    color_continuous_scale="Reds"
)
fig3.update_layout(template="plotly_white")
fig3.show()

# ── 4. CARTE DE FRANCE PAR DÉPARTEMENT ───────────────────
df_carte = pd.read_sql_query("""
    SELECT d.dept_code, d.dept_nom,
           ROUND(AVG(sd.taux_brut), 2) as taux_moyen
    FROM suicides_deces sd
    JOIN departements d ON sd.dept_code = d.dept_code
    GROUP BY d.dept_code, d.dept_nom
""", conn)

fig4 = px.choropleth(
    df_carte,
    geojson="https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements-version-simplifiee.geojson",
    locations="dept_code",
    featureidkey="properties.code",
    color="taux_moyen",
    hover_name="dept_nom",
    color_continuous_scale="Reds",
    title="🗺️ Taux de suicide par département en France",
    labels={"taux_moyen": "Taux moyen"}
)
fig4.update_geos(fitbounds="locations", visible=False)
fig4.update_layout(template="plotly_white")
fig4.show()

conn.close()
print("✅ Toutes les visualisations sont générées !")


