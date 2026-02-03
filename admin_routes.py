# Importation des fonctions du premier notebook (ou fichier services)
# Note : Dans un vrai projet, on ferait 'from admin_functions import *'
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

router = APIRouter(tags=["Stat_System"])

# 1. Route Statistiques
@router.get("/api/stats/overview")
async def stats_overview_route():
    """Calcul et renvoie les statistiques globales du dataset"""
    return get_stats_overview()

# 2. Route Client
@router.get("/api/customers/{customer_id}")
async def customer_route(customer_id: str):
    """Recherche les informations d'un client par son ID"""
    result = get_customer_summary(customer_id)
    
    if result is None:
        raise HTTPException(
            status_code=404, 
            detail=f"Le client avec l'ID {customer_id} est introuvable"
        )
    return result

# 3. Route Health (Système)
@router.get("/api/system/health")
async def health_route():
    """Vérifie le bon fonctionnement de l'API"""
    return get_system_health()

# 4. Route Metadata
@router.get("/api/system/metadata")
async def metadata_route():
    """Renvoie les informations de version du projet"""
    return {
        "version": "1.0.0",
        "last_update": "2026-02-03",
        "author": "CFMM"
    }