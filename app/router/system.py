from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import time

# --- Importation du dataset si nécessaire ---
# df = connexion_dataset()  # Si tu veux vérifier dataset_ready

# Router système
router_system = APIRouter(
    tags=["System"]
)

# Variables globales
moment_depart = time.time()
df = None  # ou df = connexion_dataset() si dataset réel

# --- Fonctions de service ---
def get_system_health() -> Dict[str, Any]:
    """Retourne l'état actuel du système"""
    uptime_s = int(time.time() - moment_depart)
    hours, rem = divmod(uptime_s, 3600)
    minutes, seconds = divmod(rem, 60)
    return {
        "status": "healthy",
        "uptime": f"{hours}h {minutes}m {seconds}s",
        "dataset_ready": df is not None
    }

def get_metadata() -> Dict[str, Any]:
    """Retourne les informations de version du projet"""
    return {
        "version": "1.0.0",
        "last_update": "2026-02-03",
        "author": "CFMM"
    }

# --- Routes ---
@router_system.get("/api/system/health")
async def health_route():
    """Vérifie le bon fonctionnement de l'API"""
    return get_system_health()

@router_system.get("/api/system/metadata")
async def metadata_route():
    """Renvoie les informations de version du projet"""
    return get_metadata()
