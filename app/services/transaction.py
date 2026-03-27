import math
from typing import Any, Dict, List, Optional
import pandas as pd
from app.config import connexion_dataset

df = connexion_dataset()


def _row_to_dict(row: pd.Series) -> Dict[str, Any]:

    return {
        "id": str(row.get("id", "")),
        "date": str(row.get("date", "")),
        "client_id": int(row["client_id"]) if pd.notna(row.get("client_id")) else None,
        "card_id": int(row["card_id"]) if pd.notna(row.get("card_id")) else None,
        "amount": float(row.get("amount", 0.0)),
        "use_chip": str(row.get("use_chip", "")),
        "merchant_id": str(row.get("merchant_id", "")),
        "merchant_city": str(row.get("merchant_city", "")),
        "merchant_state": str(row.get("merchant_state", "")),
        "mcc": str(row.get("mcc", "")),
        "mcc_description": str(row.get("mcc_description", "")),
        "errors": str(row.get("errors", "")),
        "is_fraud": int(row.get("is_fraud", 0)),
    }


def get_transactions(
    page: int = 1,
    limit: int = 5,
    type: Optional[str] = None,
    isFraud: Optional[int] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
) -> Dict[str, Any]:

    filtered_df = df.copy()

    if type:
        filtered_df = filtered_df[
            filtered_df["use_chip"].str.upper() == type.upper()
        ]

    if isFraud is not None:
        filtered_df = filtered_df[filtered_df["is_fraud"] == int(isFraud)]

    if min_amount is not None:
        filtered_df = filtered_df[filtered_df["amount"] >= min_amount]

    if max_amount is not None:
        filtered_df = filtered_df[filtered_df["amount"] <= max_amount]

    total = len(filtered_df)
    start = (page - 1) * limit
    paginated_df = filtered_df.iloc[start: start + limit]

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "results": [_row_to_dict(row) for _, row in paginated_df.iterrows()],
    }

def get_transaction_by_id(transaction_id: str) -> Optional[Dict[str, Any]]:

    if not transaction_id:
        return None

    match = df[df["id"].astype(str) == str(transaction_id).strip()]

    if match.empty:
        return None

    return _row_to_dict(match.iloc[0])


def search_transactions(payload: Dict[str, Any]) -> Dict[str, Any]:

    page = max(int(payload.get("page", 1)), 1)
    limit = max(int(payload.get("limit", 10)), 1)

    tx_type = payload.get("type")
    is_fraud = payload.get("isFraud")
    amount_range = payload.get("amount_range")

    filtered_df = df.copy()

    if tx_type:
        filtered_df = filtered_df[
            filtered_df["use_chip"].str.upper() == str(tx_type).upper()
        ]

    if is_fraud is not None:
        filtered_df = filtered_df[filtered_df["is_fraud"] == int(is_fraud)]

    if (
        amount_range
        and isinstance(amount_range, list)
        and len(amount_range) == 2
    ):
        min_amt, max_amt = float(amount_range[0]), float(amount_range[1])
        filtered_df = filtered_df[
            (filtered_df["amount"] >= min_amt) & (filtered_df["amount"] <= max_amt)
        ]

    total = len(filtered_df)
    total_pages = math.ceil(total / limit) if limit else 1
    start = (page - 1) * limit
    paginated_df = filtered_df.iloc[start: start + limit]

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
        "results": [_row_to_dict(row) for _, row in paginated_df.iterrows()],
    }


def get_transaction_types() -> List[str]:

    return sorted(df["use_chip"].dropna().unique().tolist())


def get_recent_transactions(n: int = 10) -> List[Dict[str, Any]]:

    if n <= 0:
        return []
    data = df

    data["date"] = pd.to_datetime(data["date"], errors="coerce")

    recent = data.nlargest(n, "date")

    return [_row_to_dict(row) for _, row in recent.iterrows()]


_deleted_ids: set = set()


def delete_test_transaction(transaction_id: str) -> Dict[str, Any]:

    if get_transaction_by_id(transaction_id) is None:
        return {
            "success": False,
            "message": f"Transaction '{transaction_id}' introuvable.",
        }

    _deleted_ids.add(str(transaction_id))

    return {
        "success": True,
        "message": "Transaction supprimée avec succès (mode test).",
        "deleted_transaction_id": transaction_id,
    }


def get_transactions_by_sender(
    customer_id: str,
    page: int = 1,
    limit: int = 10,
) -> Dict[str, Any]:

    subset = df[df["client_id"].astype(str) == str(customer_id)]
    total = len(subset)
    start = (page - 1) * limit
    paginated = subset.iloc[start: start + limit]

    return {
        "customer_id": customer_id,
        "page": page,
        "limit": limit,
        "total": total,
        "results": [_row_to_dict(row) for _, row in paginated.iterrows()],
    }


def get_received_transactions(
    merchant_id: str,
    page: int = 1,
    limit: int = 10,
) -> Dict[str, Any]:

    subset = df[df["merchant_id"].astype(str) == str(merchant_id)]
    total = len(subset)
    start = (page - 1) * limit
    paginated = subset.iloc[start: start + limit]

    return {
        "merchant_id": merchant_id,
        "page": page,
        "limit": limit,
        "total": total,
        "results": [_row_to_dict(row) for _, row in paginated.iterrows()],
    }