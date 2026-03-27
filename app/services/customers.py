import pandas as pd
from typing import Any, Dict, List, Optional, Union


def list_customers(df: pd.DataFrame) -> List[str]:

    return sorted(df["client_id"].dropna().unique().astype(str).tolist())


def top_customers(df: pd.DataFrame, n: int = 10) -> List[Dict[str, Any]]:

    top = (
        df.groupby("client_id", as_index=False)["amount"]
        .sum()
        .sort_values("amount", ascending=False)
        .head(n)
    )
    top["amount"] = top["amount"].round(2)
    top["client_id"] = top["client_id"].astype(str)

    return top.rename(
        columns={
            "client_id": "customer_id",
            "amount": "total_amount",
        }
    ).to_dict(orient="records")


def get_customer_profile(df: pd.DataFrame, customer_id: str) -> Optional[Dict[str, Any]]:

    subset = df[df["client_id"].astype(str) == str(customer_id)]

    if subset.empty:
        return None

    return {
        "id": customer_id,
        "transactions_count": int(len(subset)),
        "avg_amount": round(float(subset["amount"].mean()), 2),
        "total_amount": round(float(subset["amount"].sum()), 2),
        "fraudulent": bool(subset["is_fraud"].any()),
    }


def stats_by_type(df: pd.DataFrame) -> List[Dict[str, Union[str, float]]]:

    grouped = (
        df.groupby("use_chip")["amount"]
        .agg(count="count", avg_amount="mean")
        .reset_index()
        .rename(columns={"use_chip": "transaction_type"})
    )
    grouped["avg_amount"] = grouped["avg_amount"].round(2)
    grouped["count"] = grouped["count"].astype(int)

    return grouped.to_dict(orient="records")


def amount_distribution(
    df: pd.DataFrame,
    bins: Optional[List[float]] = None,
) -> Dict[str, List]:

    if bins is None:
        bins = [0, 100, 500, 1000, 5000, float("inf")]

    labels = [
        f"{int(bins[i])}-{int(bins[i + 1]) if bins[i + 1] != float('inf') else 'plus'}"
        for i in range(len(bins) - 1)
    ]

    counts = (
        pd.cut(df["amount"], bins=bins, labels=labels)
        .value_counts()
        .sort_index()
    )

    return {
        "labels": labels,
        "counts": counts.tolist(),
    }