import pandas as pd
from typing import List, Dict, Union, Optional, Any
from app.config import connexion_dataset

# Chargement initial
df_global = connexion_dataset()

def list_customers(df: pd.DataFrame) -> List[str]:
    """
    Retourne la liste unique de tous les IDs clients (expéditeurs et destinataires).
    """
    # Utilisation de .unique() sur la concaténation des valeurs pour plus de rapidité
    combined = pd.concat([df["Sender Account ID"], df["Receiver Account ID"]])
    return combined.dropna().astype(str).unique().tolist()


def top_customers(df: pd.DataFrame, n: int = 10) -> List[Dict[str, float]]:
    """
    Top N clients par montant total envoyé.
    """
    top = (
        df.groupby("Sender Account ID", as_index=False)["Transaction Amount"]
        .sum()
        .sort_values("Transaction Amount", ascending=False)
        .head(n)
    )

    return top.rename(
        columns={
            "Sender Account ID": "customer_id",
            "Transaction Amount": "total_amount"
        }
    ).to_dict(orient="records")


def stats_by_type(df: pd.DataFrame) -> List[Dict[str, Union[str, float]]]:
    """
    Statistiques par type de transaction.
    """
    grouped = (
        df.groupby("Transaction Type")["Transaction Amount"]
        .agg(
            count="count",
            avg_amount="mean"
        )
        .reset_index()
        .rename(columns={"Transaction Type": "transaction_type"})
    )

    return grouped.to_dict(orient="records")


def amount_distribution(
    df: pd.DataFrame, 
    bins: Optional[List[float]] = None
) -> Dict[str, List]:
    """
    Distribution des montants par tranches.
    """
    if bins is None:
        bins = [0, 100, 500, 1000, 5000, float("inf")]

    # Correction de la génération des labels pour éviter l'erreur sur float('inf')
    labels = []
    for i in range(len(bins) - 1):
        lower = int(bins[i])
        upper = bins[i+1]
        if upper == float('inf'):
            labels.append(f"{lower}+")
        else:
            labels.append(f"{lower}-{int(upper)}")

    counts = (
        pd.cut(df["Transaction Amount"], bins=bins, labels=labels)
        .value_counts()
        .sort_index()
    )

    return {
        "labels": labels, # Changé 'bins' en 'labels' pour être plus explicite
        "counts": counts.tolist()
    }


# 2. Résumé d'un client (Route 17)
def get_customer_summary(customer_id: str) -> Optional[Dict[str, Any]]:
    df=df_global
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