from typing import Any, Dict, List

from fastapi import APIRouter, Body, HTTPException, Request

from app.services.stats import (
    amount_distribution,
    calculer_resume_fraude,
    calculer_taux_fraude_par_type,
    obtenir_stats_journalieres_completes,
    simuler_prediction_fraude,
    stats_by_type,
)

router_stat = APIRouter(prefix="/api/stats", tags=["Stats & Analytics"])


@router_stat.get("/by-type")
def get_stats_by_type_route(request: Request) -> List[Dict[str, Any]]:

    df = request.app.state.df
    return stats_by_type(df)


@router_stat.get("/distribution")
def get_amount_distribution_route(request: Request) -> Dict[str, Any]:

    df = request.app.state.df
    return amount_distribution(df)


@router_stat.get("/daily")
def get_stats_daily_history(request: Request) -> List[Dict[str, Any]]:

    df = request.app.state.df
    return obtenir_stats_journalieres_completes(df)


@router_stat.get("/fraud/summary")
def get_fraud_summary(request: Request) -> Dict[str, Any]:

    df = request.app.state.df

    if df is None or df.empty:
        raise HTTPException(status_code=500, detail="Dataset non chargé ou vide.")

    resume = calculer_resume_fraude(df)
    if isinstance(resume, dict) and "error" in resume:
        raise HTTPException(status_code=404, detail=resume["error"])

    return resume


@router_stat.get("/fraud/by-type")
def get_fraud_by_type(request: Request) -> List[Dict[str, Any]]:

    df = request.app.state.df
    return calculer_taux_fraude_par_type(df)

@router_stat.post("/fraud/predict")
def predict_fraud(
    type: str = Body(..., embed=True, description="Type de transaction (use_chip)."),
    amount: float = Body(..., embed=True, description="Montant de la transaction."),
    oldbalanceOrg: float = Body(..., embed=True, description="Solde avant la transaction."),
    newbalanceOrig: float = Body(..., embed=True, description="Solde après la transaction."),
) -> Dict[str, Any]:

    return simuler_prediction_fraude(
        type_trans=type,
        amount=amount,
        old_bal=oldbalanceOrg,
        new_bal=newbalanceOrig,
    )