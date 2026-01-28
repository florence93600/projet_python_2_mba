from fastapi import FastAPI
import time
import pandas as pd

# --- CHARGEMENT DES DONNÉES ---
try:
    chemin=r'C:\Users\missa\OneDrive\Desktop\MBA ESG\COURS\Cours python\projet final\projet_python_2_mba\transaction_data.csv'
    df = pd.read_csv(chemin)
    donnees_pretes = True
    print("Succès : Le fichier a été chargé !")
except:
    # Si le fichier n'existe pas ou a une erreur, on met False
    donnees_pretes = False
    print("Erreur : Impossible de trouver le fichier de données.")

app = FastAPI()

@app.get("/api/stats/overview")
def stats_overview():
    # On calcule les valeurs directement depuis ton fichier 'df'
    total_transactions = int(df['Transaction ID'].count())
    # On calcule le taux de fraude (moyenne de la colonne 'isFraud')
    fraud_rate = float(df['Fraud Flag'].mean()) 
    # Moyenne de la colonne 'amount'
    avg_amount = float(df['Transaction Amount'].mean())
    # Le type de transaction le plus fréquent
    most_common_type = str(df['Transaction Type'].mode()[0])

    return {
        "total_transactions": total_transactions,
        "fraud_rate": round(fraud_rate, 5), # On arrondit pour que ce soit joli
        "avg_amount": round(avg_amount, 2),
        "most_common_type": most_common_type
    }

@app.get("/api/customers/{customer_id}")
def customer(customer_id: str):
    # On cherche le client s'il est l'expéditeur OU le destinataire
    # Le symbole | signifie "OU" en Pandas
    customer_df = df[(df['Sender Account ID'] == customer_id) | 
                   (df['Receiver Account ID'] == customer_id)]

    if customer_df.empty:
        return {"error": f"Le client {customer_id} n'a pas été trouvé"}

    return {
        "id": str(customer_id),
        "transactions_count": int(customer_df['Transaction ID'].count()),
        "avg_amount": float(round(customer_df['Transaction Amount'].mean(), 2)),
        "fraudulent": bool(any(customer_df['Fraud Flag']))
    }

# --- Routes pour notre systeme---
moment_depart = time.time()

# Route d'accueil (pour éviter le "Not Found" au démarrage)
@app.get("/")
def home():
    return {
        "message": "Bienvenue!"
    }

@app.get("/api/system/health")
def health():
    uptime_seconds = int(time.time() - moment_depart)
    
    return {
        "status": "healthy", # Indique que l'API fonctionne.
        "uptime": f"{uptime_seconds}s", # Temps de fonctionnement en secondes.
        "dataset_loaded": donnees_pretes # Confirmation que le chargement des données a réussi.
    }

@app.get("/api/system/metadata")
def metadata():
    return {
        "version": "1.0.0", # Version actuelle de ton projet
        "last_update": "2026-01-28" # Date de la dernière mise à jour
    }