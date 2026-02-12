from fastapi import FastAPI, HTTPException,Body
from fastapi import APIRouter
from app.services.customers import *
from app.services.stats import *
from app.config import connexion_dataset

router_fraude = APIRouter(prefix="/api/fraud", tags=["Fraude"])

# Chargement global du dataset
df = connexion_dataset()

# Initialisation de l'API
router_fraude = APIRouter(tags=["Fraude"])


@router_fraude.get("/api/fraud/summary")
def get_fraud_summary():

    #13-Vue d'ensemble de la fraude basée sur le dataset chargé.
   
    # On vérifie si df existe pour éviter un plantage
    if df is None or df.empty:
        raise HTTPException(status_code=500, detail="Dataset non chargé ou vide")
        
    resume = calculer_resume_fraude(df)
    
    if "error" in resume:
        raise HTTPException(status_code=404, detail=resume["error"])
        
    return resume

@router_fraude.get("/api/fraud/by-type")
def get_fraud_by_type():
  
    #14- Retourne le taux de fraude pour chaque type de transaction (Deposit, Withdrawal, etc.)
 
    resultat = calculer_taux_fraude_par_type(df)
    
    if "error" in resultat:
        raise HTTPException(status_code=404, detail=resultat["error"])
        
    return resultat


@router_fraude.post("/api/fraud/predict")
def predict_fraud(
    type: str = Body(...), 
    amount: float = Body(...), 
    oldbalanceOrg: float = Body(...), 
    newbalanceOrig: float = Body(...)
):
    
    #15-Endpoint de scoring utilisant directement les paramètres du Body.
    
    # On appelle la fonction de calcul avec les paramètres reçus
    resultat = simuler_prediction_fraude(type, amount, oldbalanceOrg, newbalanceOrig)
    
    return resultat
    

