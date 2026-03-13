import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import mysql.connector
import requests

# ── Connexion MySQL ───────────────────────────────────────
from sqlalchemy import create_engine
engine = create_engine("mysql+mysqlconnector://root:root1234@localhost/suicide_prevention")

# ── 1. Taux de suicide par département (zones de crise) ──
df_suicide = pd.read_sql("""
    SELECT d.dept_code, d.dept_nom,
           ROUND(AVG(sd.taux_brut), 2) as taux_moyen
    FROM suicides_deces sd
    JOIN departements d ON sd.dept_code = d.dept_code
    GROUP BY d.dept_code, d.dept_nom
""", engine)

# ── 2. Psychiatres ────────────────────────────────────────
df_psy = pd.read_csv("psychiatres_france.csv")
df_psy = df_psy.dropna(subset=["latitude", "longitude"])
df_psy["nom"] = df_psy["nom"].fillna("Psychiatre")
df_psy["ville"] = df_psy["ville"].fillna("")

# ── 3. GeoJSON France ─────────────────────────────────────
geojson_url = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements-version-simplifiee.geojson"
geojson = requests.get(geojson_url).json()

# ── 4. Carte choroplèthe (zones de crise) ─────────────────
fig = px.choropleth(
    df_suicide,
    geojson=geojson,
    locations="dept_code",
    featureidkey="properties.code",
    color="taux_moyen",
    color_continuous_scale="Reds",
    range_color=[df_suicide.taux_moyen.min(), df_suicide.taux_moyen.max()],
    labels={"taux_moyen": "Taux suicide"},
    title="🗺️ Zones de crise suicidaire & Présence de psychiatres en France",
)

fig.update_geos(fitbounds="locations", visible=False)

# ── 5. Ajout des psychiatres sur la carte ─────────────────
fig.add_trace(go.Scattergeo(
    lat=df_psy["latitude"],
    lon=df_psy["longitude"],
    mode="markers",
    marker=dict(
        size=8,
        color="#2196F3",
        symbol="circle",
        line=dict(color="white", width=1)
    ),
    text=df_psy["nom"] + "<br>" + df_psy["ville"],
    hovertemplate="<b>%{text}</b><extra></extra>",
    name="Psychiatres"
))

# ── 6. Mise en forme ──────────────────────────────────────
fig.update_layout(
    template="plotly_white",
    legend=dict(
        title="Légende",
        orientation="v",
        x=1.05
    ),
    coloraxis_colorbar=dict(
        title="Taux de<br>suicide",
        thickness=15
    ),
    annotations=[dict(
        text="🔴 Zones rouges = taux de suicide élevé | 🔵 Points bleus = psychiatres",
        x=0.5, y=-0.05,
        xref="paper", yref="paper",
        showarrow=False,
        font=dict(size=12)
    )]
)

fig.write_html("carte_psychiatres.html")
fig.show()
print("✅ Carte générée !")