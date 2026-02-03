import pandas as pd
import time
from typing import Dict, Any, Optional

# --- CHARGEMENT DU DATASET ---
def connexion_dataset():
    try:
        chemin = r'C:\Users\missa\OneDrive\Desktop\MBA ESG\COURS\Cours python\projet final\projet_python_2_mba\transaction_data.csv'
        df = pd.read_csv(chemin)
        donnees_pretes = True
        print("Succès : Le fichier a été chargé !")
        return df # Très important : il faut renvoyer le résultat !
    except:
        # Si le fichier n'existe pas, on définit les variables par défaut
        donnees_pretes = False
        print("Erreur : Impossible de trouver le fichier de données.")
        return None

# On appelle la fonction pour créer notre variable 'df'
df = connexion_dataset()

# Initialisation du DataFrame et du temps
df = connexion_dataset()
moment_depart = time.time()

# 1. Statistiques globales (Route 7)
def get_stats_overview() -> Dict[str, Any]:
    if df is None: return {"error": "Dataset non chargé"}
    
    return {
        "total_transactions": int(df['Transaction ID'].count()),
        "fraud_rate": round(float(df['Fraud Flag'].mean()), 5),
        "avg_amount": round(float(df['Transaction Amount'].mean()), 2),
        "most_common_type": str(df['Transaction Type'].mode()[0])
    }

# 2. Résumé d'un client (Route 17)
def get_customer_summary(customer_id: str) -> Optional[Dict[str, Any]]:
    if df is None: return None
    
    # Recherche dans les colonnes Sender et Receiver
    customer_df = df[(df['Sender Account ID'] == customer_id) | 
                     (df['Receiver Account ID'] == customer_id)]

    if customer_df.empty:
        return None

    return {
        "id": str(customer_id),
        "transactions_count": int(customer_df['Transaction ID'].count()),
        "avg_amount": float(round(customer_df['Transaction Amount'].mean(), 2)),
        "is_fraudulent_user": bool(any(customer_df['Fraud Flag']))
    }

# 3. État du système (Health)
def get_system_health() -> Dict[str, Any]:
    uptime = int(time.time() - moment_depart)
    return {
        "status": "healthy",
        "uptime": f"{uptime}s",
        "dataset_ready": df is not None
    }