import pandas as pd
from typing import Optional, Dict, Any, List
from app.config import connexion_dataset
# Chargement du dataset 
df = connexion_dataset()

#1. Liste paginée des transactions 
def get_transactions(
    page: int = 1,
    limit: int = 5,
    type: Optional[str] = None,
    isFraud: Optional[bool] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None
) -> Dict[str, Any]:

    filtered_df = df.copy()

    # Filtre par type de transaction
    if type:
        filtered_df = filtered_df[
            filtered_df["Transaction Type"].str.lower() == type.lower()
        ]

    # Filtre fraude
    if isFraud is not None:
        filtered_df = filtered_df[
            filtered_df["Fraud Flag"] == isFraud
        ]

    # Filtre montant minimum
    if min_amount is not None:
        filtered_df = filtered_df[
            filtered_df["Transaction Amount"] >= min_amount
        ]

    # Filtre montant maximum
    if max_amount is not None:
        filtered_df = filtered_df[
            filtered_df["Transaction Amount"] <= max_amount
        ]

    total = len(filtered_df)

    # Pagination
    start = (page - 1) * limit
    end = start + limit
    paginated_df = filtered_df.iloc[start:end]

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "results": paginated_df.to_dict(orient="records")
    }

#2. Détails d’une transaction par son identifiant

def get_transaction_by_id(transaction_id: str) -> Optional[Dict[str, Any]]:

    if not transaction_id:
        return None

    # Normalisation (important avec Excel)
    df["Transaction ID"] = df["Transaction ID"].astype(str).str.strip()
    transaction_id = str(transaction_id).strip()

    # Filtrage
    transaction = df.loc[df["Transaction ID"] == transaction_id]

    if transaction.empty:
        return None

    # Conversion propre en dictionnaire
    return transaction.iloc[0].to_dict()


#3 Recherche multicritère (POST avec corps JSON) 

def search_transactions(payload: Dict[str, Any]) -> Dict[str, Any]:

    page = payload.get("page", 1)
    limit = payload.get("limit", 10)
    tx_type = payload.get("type")
    is_fraud = payload.get("isFraud")
    min_amount = payload.get("min_amount")
    max_amount = payload.get("max_amount")

    filtered_df = df.copy()

    # Filtre type
    if tx_type:
        filtered_df = filtered_df[
            filtered_df["Transaction Type"].str.lower() == tx_type.lower()
        ]
 # Filtre fraude
    if is_fraud is not None:
        filtered_df = filtered_df[
            filtered_df["Fraud Flag"] == is_fraud
        ]

    # Filtre montant min
    if min_amount is not None:
        filtered_df = filtered_df[
            filtered_df["Transaction Amount"] >= min_amount
        ]

    # Filtre montant max
    if max_amount is not None:
        filtered_df = filtered_df[
            filtered_df["Transaction Amount"] <= max_amount
        ]

    total = len(filtered_df)
  # Pagination
    start = (page - 1) * limit
    end = start + limit
    paginated_df = filtered_df.iloc[start:end]

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "results": paginated_df.to_dict(orient="records")
    }

#4. Liste des types de transactions disponibles (valeurs uniques de type )

def get_transaction_types() -> List[str]:

    # Supprimer les valeurs nulles et extraire les valeurs uniques
    types = (
        df["Transaction Type"]
        .dropna()
        .unique()
        .tolist()
    )

    # Optionnel : trier les types
    return sorted(types)

#5. Description : Renvoie les N dernières transactions du dataset (paramètre n , défaut=10)
def get_recent_transactions(n: int = 10) -> list[dict]:
    if n <= 0:
        return []

    data = df.copy()

    # Si une colonne Timestamp existe, on trie par date
    if "Timestamp" in data.columns:
        data["Timestamp"] = pd.to_datetime(data["Timestamp"], errors="coerce")
        data = data.sort_values(by="Timestamp", ascending=False)

    # Sinon, on prend simplement les dernières lignes du fichier
    recent_transactions = data.head(n)

    return recent_transactions.to_dict(orient="records")


#6. Suppression d'une transaction fictive (utilisée uniquement en mode test)
def delete_test_transaction(transaction_id: str) -> Dict:
 
    global df

    # Vérifier si la transaction existe
    transaction = df[df["Transaction ID"] == transaction_id]

    if transaction.empty:
        return {
            "success": False,
            "message": "Transaction introuvable"
        }

    # Vérifier si la transaction est fictive
    if "Is Test" in df.columns:
        if not bool(transaction.iloc[0]["Is Test"]):
            return {
                "success": False,
                "message": "Suppression interdite : transaction réelle"
            }
    else:
        # Alternative : ID fictif commence par TEST_
        if not transaction_id.startswith("TEST_"):
            return {
                "success": False,
                "message": "Suppression interdite : transaction réelle"
            }

    # Suppression en mémoire
    df = df[df["Transaction ID"] != transaction_id]

    try:
        # Réécriture dans le fichier Excel
        df.to_excel(df, index=False)
    except Exception as e:
        return {
            "success": False,
            "message": f"Erreur lors de la mise à jour du fichier Excel : {e}"
        }

    return {
        "success": True,
        "message": "Transaction fictive supprimée avec succès",
        "deleted_transaction_id": transaction_id
    }


#7. Listes des transactions associées à un client (origine)
def get_transactions_by_sender(customer_id: str) -> Dict[str, Any]:
   
    #Retourne toutes les transactions envoyées par un customer donné.

    # Filtrer par expéditeur
    sender_transactions = df[
        df["Sender Account ID"] == customer_id
    ]

    total = len(sender_transactions)

    return {
        "sender_account_id": customer_id,
        "total": total,
        "results": sender_transactions.to_dict(orient="records")
    }


#8. Liste des transactions reçues par un client (destination)
def get_received_transactions(
    receiver_account_id: str
) -> Dict[str, Any]:
    
    # Filtrer par bénéficiaire
    received_transactions = df[
        df["Receiver Account ID"] == receiver_account_id
    ]

    total = len(received_transactions)

    return {
        "receiver_account_id": receiver_account_id,
        "total": total,
        "results": received_transactions.to_dict(orient="records")
    }
