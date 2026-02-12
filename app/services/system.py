import time
from typing import Dict, Any

# Initialisation au démarrage de l'application
moment_depart = time.time()

# Simulation d'un DataFrame (à remplacer par votre logique réelle)
df = None 

def get_system_health() -> Dict[str, Any]:
    # Calcul de la durée écoulée
    uptime_seconds = int(time.time() - moment_depart)
    
    return {
        "status": "healthy",
        "uptime": f"{uptime_seconds}s",
        "dataset_ready": df is not None
    }