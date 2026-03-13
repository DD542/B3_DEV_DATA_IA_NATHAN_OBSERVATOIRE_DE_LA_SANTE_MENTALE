import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sqlalchemy import create_engine
import requests

engine = create_engine("mysql+mysqlconnector://root:root1234@localhost/suicide_prevention")

# ── Données ───────────────────────────────────────────────
df_evol = pd.read_sql("""
    SELECT annee, ROUND(AVG(taux_brut), 2) as taux_moyen,
           ROUND(SUM(nb_deces), 0) as total_deces
    FROM suicides_deces GROUP BY annee ORDER BY annee
""", engine)

df_sexe = pd.read_sql("""
    SELECT sx.sexe, ROUND(AVG(sd.taux_brut), 2) as taux_moyen
    FROM suicides_deces sd JOIN dim_sexe sx ON sd.id_sexe = sx.id_sexe
    WHERE sx.sexe IN ('Hommes', 'Femmes') GROUP BY sx.sexe
""", engine)

df_age = pd.read_sql("""
    SELECT a.classe_age, ROUND(AVG(sd.taux_brut), 2) as taux_moyen
    FROM suicides_deces sd JOIN dim_age a ON sd.id_age = a.id_age
    GROUP BY a.classe_age ORDER BY taux_moyen DESC
""", engine)

df_region = pd.read_sql("""
    SELECT d.region_nom, ROUND(AVG(sd.taux_brut), 2) as taux_moyen
    FROM suicides_deces sd JOIN departements d ON sd.dept_code = d.dept_code
    WHERE d.region_nom IS NOT NULL
    GROUP BY d.region_nom ORDER BY taux_moyen DESC
    LIMIT 12
""", engine)

df_top10 = pd.read_sql("""
    SELECT d.dept_nom, ROUND(AVG(sd.taux_brut), 2) as taux_moyen
    FROM suicides_deces sd JOIN departements d ON sd.dept_code = d.dept_code
    GROUP BY d.dept_nom ORDER BY taux_moyen DESC LIMIT 10
""", engine)

df_carte = pd.read_sql("""
    SELECT d.dept_code, d.dept_nom, ROUND(AVG(sd.taux_brut), 2) as taux_moyen
    FROM suicides_deces sd JOIN departements d ON sd.dept_code = d.dept_code
    GROUP BY d.dept_code, d.dept_nom
""", engine)

df_psy = pd.read_csv("psychiatres_france.csv").dropna(subset=["latitude", "longitude"])

geojson = requests.get(
    "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements-version-simplifiee.geojson"
).json()

# ── Dashboard ─────────────────────────────────────────────
fig = make_subplots(
    rows=3, cols=2,
    subplot_titles=(
        "📈 Évolution annuelle du taux de suicide",
        "👥 Comparaison Hommes vs Femmes",
        "🎂 Taux de suicide par classe d'âge",
        "🌍 Taux de suicide par région",
        "🏆 Top 10 départements les plus touchés",
        "📊 Total décès par année"
    ),
    specs=[
        [{"type": "scatter"}, {"type": "bar"}],
        [{"type": "bar"},     {"type": "bar"}],
        [{"type": "bar"},     {"type": "bar"}],
    ],
    vertical_spacing=0.12,
    horizontal_spacing=0.1
)

# Graphique 1 - Évolution
fig.add_trace(go.Scatter(
    x=df_evol["annee"], y=df_evol["taux_moyen"],
    mode="lines+markers",
    line=dict(color="#E63946", width=3),
    marker=dict(size=10),
    name="Taux moyen"
), row=1, col=1)

# Graphique 2 - Sexe
fig.add_trace(go.Bar(
    x=df_sexe["sexe"], y=df_sexe["taux_moyen"],
    marker_color=["#1D3557", "#E63946"],
    name="Sexe"
), row=1, col=2)

# Graphique 3 - Âge
fig.add_trace(go.Bar(
    x=df_age["classe_age"], y=df_age["taux_moyen"],
    marker_color="#E63946",
    name="Âge"
), row=2, col=1)

# Graphique 4 - Région
fig.add_trace(go.Bar(
    x=df_region["taux_moyen"], y=df_region["region_nom"],
    orientation="h",
    marker_color="#457B9D",
    name="Région"
), row=2, col=2)

# Graphique 5 - Top 10
fig.add_trace(go.Bar(
    x=df_top10["taux_moyen"], y=df_top10["dept_nom"],
    orientation="h",
    marker_color="#E63946",
    name="Top 10"
), row=3, col=1)

# Graphique 6 - Total décès
fig.add_trace(go.Bar(
    x=df_evol["annee"], y=df_evol["total_deces"],
    marker_color="#1D3557",
    name="Total décès"
), row=3, col=2)

# ── Mise en forme ─────────────────────────────────────────
fig.update_layout(
    title=dict(
        text="🧠 Observatoire de la Santé Mentale — Dashboard Suicide en France",
        font=dict(size=20),
        x=0.5
    ),
    height=1200,
    template="plotly_white",
    showlegend=False
)

# ── Export HTML ───────────────────────────────────────────
fig.write_html("dashboard.html")
fig.show()
print("✅ Dashboard sauvegardé dans dashboard.html")