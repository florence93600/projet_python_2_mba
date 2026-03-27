# 🏦 Banking Transactions API

**FastAPI 0.110+** | **Python 3.12+** 

## 1. Présentation du Projet
Cette API REST robuste est conçue pour manipuler et analyser des données de transactions bancaires réelles. Grâce à une **Clean Architecture**, elle permet la recherche multicritère, le scoring de fraude et l'analyse statistique sur un volume de 1,42 Go de données.

Les données sont extraites dynamiquement via l'API Kaggle : [Source Kaggle](https://www.kaggle.com/datasets/computingvictor/transactions-fraud-datasets).

| Module | Fonctionnalités |
| :--- | :--- |
| **Transactions** | Lecture, pagination, filtrage dynamique (Body JSON). |
| **Statistiques** | Agrégations temporelles et distributions des montants. |
| **Fraude** | Calcul des taux de risque et scoring prédictif (`/predict`). |
| **Clients** | Analyse comportementale par profil utilisateur. |
| **Système** | Healthcheck et métadonnées du dataset chargé. |

## 2. Structure du Projet (Arborescence)
```text
PROJET_PYTHON_2_MBA/
├── app/
│   ├── router/          # Couche Transport (Endpoints)
│   ├── services/        # Couche Métier (Logique Pandas)
│   ├── config.py        # Adapter KaggleHub (Chargement dynamique)
│   └── main.py          # Point d'entrée & State global
├── data/                # Référentiel Data (Virtuel)
│   ├── données_transactions.csv
│   ├── données_utilisateurs.csv
│   └── données_cartes.csv
├── tests/               # Suite de tests unitaires (Pytest)
├── README.md
└── requirements.txt     # Dépendances (kagglehub, pandas, fastapi)
```

## 3. Installation et Lancement

### Clonage et dépendances
```bash
git clone https://github.com/florence93600/projet_python_2_mba.git
cd projet_python_2_mba

python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

### Lancement du serveur
```bash
uvicorn app.main:app --reload
```
Documentation interactive disponible sur : `http://127.0.0.1:8000/docs`

```bash
pytest tests/
pytest --cov=app tests/ --cov-report=term-missing
```

## 4. Collaboration (Git Flow)
* **Main / Developer :** Branches de production et d'intégration.
* **Features :** Branches nominatives (Florence, Marie-Paule, Carole, Sylvain).

## 5. Livraison
**Format :** Package Python modulaire avec tests unitaires automatisés via Pull Request GitHub.
