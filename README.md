<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f4f7f6;
        }
        h1 { color: #005571; border-bottom: 2px solid #005571; padding-bottom: 10px; }
        h2 { color: #0078d4; margin-top: 30px; border-left: 5px solid #0078d4; padding-left: 10px; }
        h3 { color: #2d3e50; }
        code {
            background-color: #272822;
            color: #f8f8f2;
            padding: 2px 5px;
            border-radius: 4px;
            font-family: 'Courier New', Courier, monospace;
        }
        pre {
            background-color: #272822;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th { background-color: #005571; color: white; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        .badge {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 20px;
            color: white;
            font-size: 0.8em;
            font-weight: bold;
            margin-right: 5px;
        }
        .badge-fastapi { background-color: #05998b; }
        .badge-python { background-color: #3776ab; }
        .badge-coverage { background-color: #4c1; }
    </style>
</head>
<body>

    <h1>🏦 Banking Transactions API</h1>
    
    <div>
        <span class="badge badge-fastapi">FastAPI 0.110+</span>
        <span class="badge badge-python">Python 3.12+</span>
        <span class="badge badge-coverage">Coverage 93%</span>
    </div>

    <h2>1. Présentation du Projet</h2>
    <p>
        Cette API REST robuste est conçue pour manipuler et analyser des données de transactions bancaires réelles. 
        Grâce à une <strong>Clean Architecture</strong>, elle permet la recherche multicritère, le scoring de fraude et l'analyse statistique sur un volume de 1,42 Go de données.
    </p>

    <p>
        Les données sont extraites dynamiquement via l'API Kaggle : 
        <a href="https://www.kaggle.com/datasets/computingvictor/transactions-fraud-datasets">Source Kaggle</a>.
    </p>

    <table>
        <thead>
            <tr>
                <th>Module</th>
                <th>Fonctionnalités</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Transactions</strong></td>
                <td>Lecture, pagination, filtrage dynamique (Body JSON).</td>
            </tr>
            <tr>
                <td><strong>Statistiques</strong></td>
                <td>Agrégations temporelles et distributions des montants.</td>
            </tr>
            <tr>
                <td><strong>Fraude</strong></td>
                <td>Calcul des taux de risque et scoring prédictif (<code>/predict</code>).</td>
            </tr>
            <tr>
                <td><strong>Clients</strong></td>
                <td>Analyse comportementale par profil utilisateur.</td>
            </tr>
            <tr>
                <td><strong>Système</strong></td>
                <td>Healthcheck et métadonnées du dataset chargé.</td>
            </tr>
        </tbody>
    </table>

    <h2>2. Structure du Projet (Arborescence)</h2>
    <pre>
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
    </pre>

    <h2>3. Installation et Lancement</h2>
    <h3>Clonage et dépendances</h3>
    <pre>
git clone https://github.com/florence93600/projet_python_2_mba.git
cd projet_python_2_mba

python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
    </pre>

    <h3>Lancement du serveur</h3>
    <pre>uvicorn app.main:app --reload</pre>
    <p>Documentation interactive disponible sur : <code>http://127.0.0.1:8000/docs</code></p>

    <h2>4. Tests et Qualité</h2>
    <p>Le projet garantit une fiabilité élevée avec une couverture de tests de 93%.</p>
    <pre>
pytest tests/
pytest --cov=app tests/ --cov-report=term-missing
    </pre>

    <h2>5. Collaboration (Git Flow)</h2>
    <ul>
        <li><strong>Main / Developer :</strong> Branches de production et d'intégration.</li>
        <li><strong>Features :</strong> Branches nominatives (Florence, Marie-Paule, Carole, Sylvain).</li>
    </ul>

    <h2>6. Livraison</h2>
    <p>Format : Package Python modulaire avec tests unitaires automatisés via Pull Request GitHub.</p>

</body>
</html>