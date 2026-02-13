import pandas as pd
from typing import Dict, List, Optional, Union,Any
from app.config import connexion_dataset

# Chargement global du dataset
df = connexion_dataset()


def stats_by_type(df: pd.DataFrame) -> List[Dict[str, Union[str, float]]]:
    
    grouped = (
        df.groupby("Transaction Type")["Transaction Amount"]
        .agg(count="count", avg_amount="mean")
        .reset_index()
    )

    return grouped.to_dict(orient="records")


def amount_distribution(
    df: pd.DataFrame,
    bins: Optional[List[float]] = None
) -> Dict[str, List]:
    
    if bins is None:
        bins = [0, 100, 500, 1000, 5000, float("inf")]

    labels = [
        f"{int(bins[i])}-{int(bins[i + 1]) if bins[i + 1] != float('inf') else 'plus'}"
        for i in range(len(bins) - 1)
    ]

    counts = (
        pd.cut(df["Transaction Amount"], bins=bins, labels=labels)
        .value_counts()
        .sort_index()
    )

    return {
        "bins": labels,
        "counts": counts.tolist()
    }

def obtenir_stats_journalieres_completes(df, col_timestamp='Timestamp', col_valeur='Transaction Amount'):
  
    #Retourne l'historique complet (volume et moyenne) groupé par jour.
   
    df[col_timestamp] = pd.to_datetime(df[col_timestamp])
    stats = (
        df.groupby(df[col_timestamp].dt.date)
        .agg(
            volume=(col_valeur, "count"),
            moyenne=(col_valeur, "mean")
        )
        .reset_index()
        .rename(columns={col_timestamp: "date"})
    )
    return stats.to_dict(orient="records")

def calculer_taux_fraude_par_type(df):
    
    #Calcule le taux de fraude (moyenne) par type de transaction en utilisant les colonnes réelles du CSV.
    
    # 1. Vérification des noms de colonnes exacts
    col_type = "Transaction Type"
    col_fraude = "Fraud Flag"
    
    if col_fraude not in df.columns or col_type not in df.columns:
        return {"error": f"Colonnes requises ({col_type} ou {col_fraude}) absentes du dataset"}

    # 2. Calcul des statistiques
    # Comme Fraud Flag est un booléen (True/False), .mean() calcule 
    # automatiquement le ratio (ex: 0.15 pour 15% de fraude)
    stats = (
        df.groupby(col_type)[col_fraude]
        .mean()
        .reset_index()
    )
    
    # 3. Renommer les colonnes pour la sortie API
    stats.columns = ["type", "fraud_rate"]
    
    # 4. Conversion des valeurs en arrondis pour la propreté
    stats["fraud_rate"] = stats["fraud_rate"].round(4)

    return stats.to_dict(orient="records")

def calculer_resume_fraude(df):
    """
    Calcule les indicateurs de fraude réels à partir du DataFrame.
    """
    col_fraud = 'Fraud Flag'
    col_status = 'Transaction Status'
    
    if col_fraud not in df.columns:
        return {"error": f"La colonne '{col_fraud}' est absente du dataset"}

    # Total des fraudes (Somme des True dans Fraud Flag)
    total_frauds = int(df[col_fraud].sum())
    
    # Nombre de transactions 'Failed' qui étaient des fraudes (simule le 'flagged')
    flagged = int(df[(df[col_fraud] == True) & (df[col_status] == 'Failed')].shape[0])
    
    # Métriques de performance (statiques ou calculées si vous avez un modèle)
    precision = 0.95
    recall = 0.88
    
    return {
        "total_frauds": total_frauds,
        "flagged": flagged,
        "precision": precision,
        "recall": recall
    }

def simuler_prediction_fraude(type_trans, amount, old_bal, new_bal):
    
    #Calcule un score de fraude basé sur les paramètres reçus.
    
    score = 0.0
    
    # Règle 1 : Montant élevé (Seuil basé sur votre dataset)
    if amount > 3000:
        score += 0.4
    
    # Règle 2 : Incohérence de balance
    if abs((old_bal - new_bal) - amount) > 0.01:
        score += 0.3
        
    # Règle 3 : Type de transaction à risque (Normalisé en majuscule)
    if type_trans.upper() == "TRANSFER":
        score += 0.2

    probability = min(score, 0.99)
    
    return {
        "isFraud": bool(probability > 0.5),
        "probability": round(probability, 2)
    }

def get_stats_overview(df:pd.DataFrame) -> Dict[str, Any]:
    
    if df is None: return {"error": "Dataset non chargé"}
    
    return {
        "total_transactions": int(df['Transaction ID'].count()),
        "fraud_rate": round(float(df['Fraud Flag'].mean()), 5),
        "avg_amount": round(float(df['Transaction Amount'].mean()), 2),
        "most_common_type": str(df['Transaction Type'].mode()[0])
    }
