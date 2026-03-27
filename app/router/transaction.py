from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, HTTPException, Query

from app.services.transaction import (
    delete_test_transaction,
    get_recent_transactions,
    get_received_transactions,
    get_transaction_by_id,
    get_transaction_types,
    get_transactions,
    get_transactions_by_sender,
    search_transactions,
)

router = APIRouter(tags=["Transaction"])

@router.get("/api/transactions/types")
async def transaction_types_route() -> Dict[str, Any]:
    """Retourne les valeurs uniques de la colonne use_chip.

    Returns
    -------
    dict
        Dictionnaire avec ``types`` et ``total_types``.
    """
    types: List[str] = get_transaction_types()
    return {
        "success": True,
        "total_types": len(types),
        "types": types,
    }


# 5. N dernières transactions
@router.get("/api/transactions/recent")
async def recent_transactions_route(
    n: int = Query(10, ge=1, description="Nombre de dernières transactions à récupérer"),
) -> Dict[str, Any]:

    recent = get_recent_transactions(n)
    return {
        "success": True,
        "total": len(recent),
        "transactions": recent,
    }


@router.post("/api/transactions/search")
async def search_transactions_route(
    page: int = Body(1, ge=1, description="Numéro de page"),
    limit: int = Body(10, ge=1, description="Nombre de résultats par page"),
    tx_type: Optional[str] = Body(None, description="Type de transaction (use_chip)"),
    isFraud: Optional[int] = Body(None, ge=0, le=1, description="Filtre fraude : 0 ou 1"),
    amount_range: Optional[List[float]] = Body(None, description="[montant_min, montant_max]"),
) -> Dict[str, Any]:

    filters: Dict[str, Any] = {
        "page": page,
        "limit": limit,
        "type": tx_type,
        "isFraud": isFraud,
        "amount_range": amount_range,
    }
    result = search_transactions(filters)
    return {
        "success": True,
        "filters_applied": filters,
        "data": result,
    }


@router.get("/api/transactions/by-customer/{customer_id}")
async def transactions_by_sender_route(
    customer_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
) -> Dict[str, Any]:

    result = get_transactions_by_sender(customer_id, page=page, limit=limit)
    return {
        "success": True,
        "filters_applied": {"customer_id": customer_id},
        "data": result,
    }

@router.get("/api/transactions/to-customer/{customer_id}")
async def received_transactions_route(
    customer_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
) -> Dict[str, Any]:

    result = get_received_transactions(customer_id, page=page, limit=limit)
    return {
        "success": True,
        "filters_applied": {"merchant_id": customer_id},
        "data": result,
    }


@router.get("/api/transactions/{id}")
async def get_transaction_by_id_route(id: str) -> Dict[str, Any]:

    transaction = get_transaction_by_id(id)
    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail=f"Transaction avec ID '{id}' introuvable.",
        )
    return {"success": True, "transaction": transaction}


@router.get("/api/transactions")
async def transaction_route(
    page: int = Query(1, ge=1, description="Numéro de page"),
    limit: int = Query(5, ge=1, description="Nombre de résultats par page"),
    type: Optional[str] = Query(None, description="Type de transaction (use_chip)"),
    isFraud: Optional[int] = Query(None, ge=0, le=1, description="Filtre fraude : 0 ou 1"),
    min_amount: Optional[float] = Query(None, description="Montant minimum"),
    max_amount: Optional[float] = Query(None, description="Montant maximum"),
) -> Dict[str, Any]:

    result = get_transactions(
        page=page,
        limit=limit,
        type=type,
        isFraud=isFraud,
        min_amount=min_amount,
        max_amount=max_amount,
    )
    return {
        "success": True,
        "filters_applied": {
            "page": page,
            "limit": limit,
            "type": type,
            "isFraud": isFraud,
            "min_amount": min_amount,
            "max_amount": max_amount,
        },
        "data": result,
    }


@router.delete("/api/transactions/{transaction_id}")
async def delete_test_transaction_route(transaction_id: str) -> Dict[str, Any]:

    result = delete_test_transaction(transaction_id)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("message"))
    return {
        "success": True,
        "deleted_transaction_id": transaction_id,
        "message": result.get("message"),
    }