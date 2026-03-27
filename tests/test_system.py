import pandas as pd
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.router.system import router_system  # adapte le chemin si besoin


def create_test_app(df=None):
    app = FastAPI()
    app.include_router(router_system)

    # Injection du DataFrame dans l'état de l'app
    app.state.df = df

    return app


def test_health_route_with_dataframe():
    df = pd.DataFrame({"col": [1, 2, 3]})
    app = create_test_app(df)

    client = TestClient(app)
    response = client.get("/api/system/health")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "healthy"
    assert data["dataset_ready"] is True
    assert data["total_records"] == 3
    assert "uptime" in data
    assert "timestamp" in data


def test_health_route_without_dataframe():
    app = create_test_app(None)

    client = TestClient(app)
    response = client.get("/api/system/health")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "degraded"
    assert data["dataset_ready"] is False
    assert data["total_records"] == 0


def test_health_route_missing_state_df():
    app = FastAPI()
    app.include_router(router_system)

    client = TestClient(app)
    response = client.get("/api/system/health")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "degraded"


def test_metadata_route():
    app = create_test_app()

    client = TestClient(app)
    response = client.get("/api/system/metadata")

    assert response.status_code == 200
    data = response.json()

    assert data["version"] == "1.0.0"
    assert data["author"] == "CFMM"
    assert data["environment"] == "Production"