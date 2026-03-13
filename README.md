# 🧠 Observatoire de la Santé Mentale — Suicide en France

## 📌 Description
Projet d'analyse de données sur le suicide en France.
Collecte, intégration, stockage, analyse et visualisation de données
issues de Santé Publique France, du CépiDc-Inserm et du SNDS.

---

## 👥 Équipe
- Nathan — B3 Dev Data IA

---

## 🗂️ Sources de données
| Source | Type | Contenu |
|---|---|---|
| Santé Publique France | CSV | Passages aux urgences pour gestes auto-infligés |
| CépiDc-Inserm | CSV | Décès par suicide par département |
| SNDS | CSV | Hospitalisations pour gestes auto-infligés |
| OpenStreetMap | Scraping | Localisation des psychiatres en France |
| geo.api.gouv.fr | API | Population par département |

---

## 🗄️ Structure de la base de données
```
suicide_prevention (MySQL)
├── departements        → 103 départements français
├── dim_age             → 5 classes d'âge
├── dim_sexe            → 3 catégories (Hommes/Femmes/H+F)
├── urgences_gestes     → 7 725 lignes
├── suicides_deces      → 7 725 lignes
└── hospit_gestes       → 9 270 lignes
```

---

## 📁 Fichiers du projet
| Fichier | Description |
|---|---|
| `ingestion.py` | Chargement des CSV dans MySQL |
| `scraping_psychiatres.py` | Scraping OpenStreetMap |
| `api_insee.py` | Consommation API geo.api.gouv.fr |
| `analyses_sql.py` | Requêtes SQL + export CSV |
| `visualisations.py` | 5 graphiques Plotly |
| `carte_psychiatres.py` | Carte zones de crise + psychiatres |
| `dashboard.py` | Dashboard interactif final |
| `api.py` | API REST Flask |

---

## 🚀 Installation et lancement

### 1. Installer les dépendances
```bash
pip install pandas mysql-connector-python sqlalchemy
pip install plotly flask flask-cors requests beautifulsoup4
```

### 2. Créer la base de données MySQL
```sql
CREATE DATABASE suicide_prevention;
```

### 3. Ingérer les données
```bash
python ingestion.py
```

### 4. Lancer l'API
```bash
python api.py
```

### 5. Lancer le dashboard
```bash
python dashboard.py
```

---

## 🌐 Endpoints API

| Endpoint | Description |
|---|---|
| `GET /api/departements` | Liste tous les départements |
| `GET /api/deces` | Taux de suicide par département |
| `GET /api/top10` | Top 10 départements les plus touchés |
| `GET /api/evolution` | Évolution annuelle nationale |
| `GET /api/region/<nom>` | Stats d'une région |
| `GET /api/psychiatres` | Liste des psychiatres scrapés |

---

## 📊 Principaux résultats

- 🔴 **Bretagne** est la région la plus touchée (taux moyen : 19.46)
- 🔴 **Côtes-d'Armor** est le département le plus touché (taux : 22.59)
- 📈 Légère hausse nationale entre 2019 et 2022
- 👥 Les **hommes** sont 3x plus touchés que les femmes
- 🏥 Certaines zones de crise ont **peu ou pas de psychiatres**

---

## 🔗 Visualisations
- [Dashboard interactif](dashboard.html)
- [Carte zones de crise + psychiatres](carte_psychiatres.html)
