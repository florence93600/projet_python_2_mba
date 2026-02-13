from fastapi import FastAPI, HTTPException,Body
from fastapi import APIRouter
from app.services.customers import *
from app.services.stats import *
from app.config import connexion_dataset

router_stat = APIRouter(prefix="/api/customers", tags=["Customers"])

# Chargement global du dataset
df = connexion_dataset()

@router_stat.get("/api/stats/daily", tags=["Statistiques"])
def get_stats_daily_history():
    #12- Retourne l'historique complet des stats groupées par jour.
    return obtenir_stats_journalieres_completes(df)

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

