from app.services.transaction import *
from fastapi import APIRouter, Query, Body,HTTPException
from typing import Optional, Dict, Any
from app.services.stats import *
router = APIRouter(tags=["Transaction"])

@router.get("/api/transactions/stats")
def get_stats_by_type():
    return stats_by_type(df)


@router.get("/api/transactions/distribution")
def get_amount_distribution():
    return amount_distribution(df)

#1. Liste paginée des transactions 
@router.get("/api/transactions")
async def transaction_route(
    page: int = Query(1, description="Numéro de page"),
    limit: int = Query(5, description="Nombre de résultats par page"),
    tx_id: Optional[str] = Query(None, description="ID de la transaction"),
    tx_type: Optional[str] = Query(None, description="Type de la transaction"),
    amount: Optional[float] = Query(None, description="Montant minimum de la transaction"),
    isFraud: Optional[bool] = Query(None, description="Filtre fraude")
):
    
    # Appel dynamique de la fonction get_transactions
    result = get_transactions(
        page=page,
        limit=limit,
        type=tx_type,
        min_amount=amount,
        isFraud=isFraud
    )

    return {
        "success": True,
        "filters_applied": {
            "page": page,
            "limit": limit,
            "id": tx_id,
            "type": tx_type,
            "min_amount": amount,
            "isFraud": isFraud
        },
        "data": result
    }

#4. Liste des types de transactions disponibles (valeurs uniques de type )
@router.get("/api/transactions/types")
async def transaction_types_route() -> Dict[str, Any]:
    
    types = get_transaction_types()

    return {
        "success": True,
        "total_types": len(types),
        "types": types
    }

#5. Description : Renvoie les N dernières transactions du dataset (paramètre n , défaut=10)
@router.get("/api/transactions/recent")
async def recent_transactions_route(
    n: int = Query(10, description="Nombre de dernières transactions à récupérer")
) -> Dict[str, Any]:

    if n <= 0:
        return {"success": True, "total": 0, "transactions": []}

    recent_transactions = get_recent_transactions(n)

    return {
        "success": True,
        "total": len(recent_transactions),
        "transactions": recent_transactions
    }

#2. Détails d’une transaction par son identifiant
@router.get("/api/transactions/{id}")
async def get_transaction_by_id_route(id: str):
    transaction = get_transaction_by_id(id)

    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail=f"Transaction avec ID '{id}' introuvable"
        )

    return {
        "success": True,
        "transaction": transaction
    }
#3 Recherche multicritère (POST avec corps JSON) 
@router.post("/api/transactions/search")
async def search_transactions_route(
    page: int = Body(1, description="Numéro de page"),
    limit: int = Body(10, description="Nombre de résultats par page"),
    tx_type: Optional[str] = Body(None, description="Type de la transaction"),
    isFraud: Optional[bool] = Body(None, description="Filtre fraude"),
    min_amount: Optional[float] = Body(None, description="Montant minimum"),
    max_amount: Optional[float] = Body(None, description="Montant maximum")
):
    
    # Construire le dictionnaire attendu par search_transactions
    filters = {
        "page": page,
        "limit": limit,
        "type": tx_type,
        "isFraud": isFraud,
        "min_amount": min_amount,
        "max_amount": max_amount
    }

    # Appel de la fonction
    result = search_transactions(filters)

    return {
        "success": True,
        "filters_applied": filters,
        "data": result
    }

#6. Suppression d'une transaction fictive (utilisée uniquement en mode test)

@router.delete("/api/transactions/{transaction_id}")
async def delete_test_transaction_route(transaction_id: str):
    result = delete_test_transaction(transaction_id)

    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("message")
        )

    return {
        "success": True,
        "deleted_transaction_id": transaction_id,
        "message": result.get("message")
    }

#7. Listes des transactions associées à un client (origine)

@router.get("/api/transactions/by-customer/{customer_id}") 
async def transactions_by_sender_route(customer_id: str) -> Dict[str, Any]:
    #Récupère toutes les transactions envoyées par un expéditeur spécifique.

    result = get_transactions_by_sender(customer_id)

    return {
        "success": True,
        "filters_applied": {
            "sender_account_id": customer_id
        },
        "data": result
    }

#8. Liste des transactions reçues par un client (destination)

@router.get("/api/transactions/to-customer/{customer_id}")
async def received_transactions_route(
    customer_id: str
) -> Dict[str, Any]:
    
    result = get_received_transactions(customer_id)

    return {
        "success": True,
        "filters_applied": {
            "receiver_account_id": customer_id
        },
        "data": result
    }