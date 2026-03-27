from typing import Any, Dict

from fastapi import APIRouter, Body, HTTPException, Request

from app.services.stats import (
    calculer_resume_fraude,
    calculer_taux_fraude_par_type,
    simuler_prediction_fraude,
)

router_fraude = APIRouter(prefix="/api/fraud", tags=["Fraude"])


@router_fraude.get("/summary")
def get_fraud_summary(request: Request) -> Dict[str, Any]:

    df = request.app.state.df

    if df is None or df.empty:
        raise HTTPException(status_code=500, detail="Dataset non chargé ou vide.")

    resume = calculer_resume_fraude(df)

    if isinstance(resume, dict) and "error" in resume:
        raise HTTPException(status_code=404, detail=resume["error"])

    return resume


@router_fraude.get("/by-type")
def get_fraud_by_type(request: Request) -> Any:

    df = request.app.state.df

    resultat = calculer_taux_fraude_par_type(df)

    if isinstance(resultat, dict) and "error" in resultat:
        raise HTTPException(status_code=404, detail=resultat["error"])

    return resultat


@router_fraude.post("/predict")
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