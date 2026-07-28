# Weather Big Data / DevOps Project — ESGI

End-to-end DevOps & Data Engineering project: ingest free weather data
(Open-Meteo), clean it with pandas, visualize it in Streamlit, then deploy
to Azure with Terraform (remote state + Key Vault) via a CI/CD pipeline.

## Roadmap

| Étape | Contenu | Statut |
|-------|---------|--------|
| 1 | Application Python météo en local (ETL) | ✅ en cours |
| 2 | Dashboard Streamlit (`app.py`) | ✅ |
| 3 | Dockerisation | ✅ |
| 4 | Structure Git & `.gitignore` | ✅ |
| 5 | Terraform base + remote state Azure | ⏳ |
| 6 | Terraform complet + Key Vault | ⏳ |
| 7 | Pipeline CI | ⏳ |
| 8 | Pipeline CD | ⏳ |
| 9 | Démo live + livrables | ⏳ |

## Arborescence

```
project/
├── data/
│   ├── raw/         # Landing zone : payloads JSON bruts de l'API
│   └── processed/   # Gold zone    : CSV nettoyé (pandas)
├── src/
│   ├── extract.py   # Appel API Open-Meteo -> JSON brut
│   ├── transform.py # Nettoyage/typage pandas -> CSV
│   └── pipeline.py  # Orchestration ETL (extract -> transform -> load)
├── tests/
│   ├── test_extract.py
│   └── test_transform.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Étape 1 — Pipeline ETL en local

### Installation

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Exécution

```powershell
# ETL complet : télécharge, nettoie, écrit data/raw + data/processed
python -m src.pipeline

# Localisation personnalisée (ex : Lyon, 5 jours de prévision)
python -m src.pipeline --lat 45.75 --lon 4.85 --days 5
```

Sorties :
- `data/raw/weather_raw_<timestamp>.json` — payload brut (Landing).
- `data/processed/weather_clean.csv` — données nettoyées (Gold).

### Tests

```powershell
pytest -v
```

Les tests mockent l'appel HTTP (aucun réseau requis) et valident la logique
pandas (renommage, typage, tri, déduplication, écriture CSV).

## Étape 2 — Dashboard Streamlit

```powershell
streamlit run app.py
```

Ouvre http://localhost:8501. Le dashboard :
- lit `data/processed/weather_clean.csv` (le génère si absent) ;
- affiche 4 KPIs (temp. moyenne/max, précip. totales, vent moyen) ;
- graphiques : température, précipitations, vent + humidité ;
- carte de la ville sélectionnée + table des données brutes ;
- sélecteur de ville + bouton **Rafraîchir** qui relance le pipeline ETL.

## Étape 3 — Dockerisation

Image `python:3.11-slim`, utilisateur **non-root** (`appuser`), healthcheck sur
`/_stcore/health`, cache des dépendances.

```powershell
# Avec docker compose (recommandé)
docker compose up --build
# -> http://localhost:8501

# Ou en direct
docker build -t weather-dashboard:local .
docker run -p 8501:8501 -v ${PWD}/data:/app/data weather-dashboard:local
```

Le volume `./data:/app/data` persiste les zones Landing/Gold sur l'hôte.

## Source de données

[Open-Meteo](https://open-meteo.com/) — API météo gratuite, **sans clé API**.
Variables horaires : température, humidité, précipitations, vitesse du vent.

## Conventions de branches Git

- `main` — branche stable, protégée.
- `feature/add-*` — ajout de fonctionnalité (ex : `feature/add-streamlit`).
- `feature/modif-*` — modification existante (ex : `feature/modif-dockerfile`).

## Sécurité

Aucun secret en clair dans le dépôt. Les clés/identités Azure seront gérées
via Azure Key Vault et Service Principals / Managed Identities (étapes 5-6).
