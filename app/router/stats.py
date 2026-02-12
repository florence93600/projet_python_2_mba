from fastapi import FastAPI, HTTPException,Body
from fastapi import APIRouter
from app.services.customers import *
from app.services.stats import *
from app.config import connexion_dataset

router_stat = APIRouter(prefix="/api/customers", tags=["Customers"])

# Chargement global du dataset
df = connexion_dataset()

# Initialisation de l'API
router_stat = APIRouter(tags=["Stats"])


@router_stat.get("/api/stats/daily")
def get_stats_daily_history():
    #12- Retourne l'historique complet des stats groupées par jour.
    return obtenir_stats_journalieres_completes(df)

@router_stat.get("/api/fraud/summary")
def get_fraud_summary():

    #13-Vue d'ensemble de la fraude basée sur le dataset chargé.
   
    # On vérifie si df existe pour éviter un plantage
    if df is None or df.empty:
        raise HTTPException(status_code=500, detail="Dataset non chargé ou vide")
        
    resume = calculer_resume_fraude(df)
    
    if "error" in resume:
        raise HTTPException(status_code=404, detail=resume["error"])
        
    return resume

@router_stat.get("/api/fraud/by-type")
def get_fraud_by_type():
  
    #14- Retourne le taux de fraude pour chaque type de transaction (Deposit, Withdrawal, etc.)
 
    resultat = calculer_taux_fraude_par_type(df)
    
    if "error" in resultat:
        raise HTTPException(status_code=404, detail=resultat["error"])
        
    return resultat


@router_stat.post("/api/fraud/predict")
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

@router_stat.get("/api/stats/by-type")
def get_stats_by_type():
    return stats_by_type(df)

@router_stat.get("/api/stats/amount-distribution")
def get_amount_distribution():
    return amount_distribution(df)     

@router_stat.get("/api/stats/overview")
async def stats_overview_route():
    """Calcul et renvoie les statistiques globales du dataset"""
    return get_stats_overview()    

