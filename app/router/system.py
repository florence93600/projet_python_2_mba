from fastapi import APIRouter, Request
from typing import Dict, Any
from app.services.system import get_system_health # On importe le service corrigé

router_system = APIRouter(
    tags=["System"]
)

def get_metadata() -> Dict[str, Any]:

    return {
        "version": "1.0.0",
        "last_update": "2026-02-03",
        "author": "CFMM",
        "environment": "Production"
    }


@router_system.get("/api/system/health")
async def health_route(request: Request):

    df = getattr(request.app.state, "df", None)

    return get_system_health(df)


@router_system.get("/api/system/metadata")
async def metadata_route():

    return get_metadata()