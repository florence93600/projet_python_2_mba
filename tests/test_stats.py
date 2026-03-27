import pytest
import pandas as pd
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch


# ─── App factory ──────────────────────────────────────────────────────────────

def make_app(df: pd.DataFrame) -> FastAPI:
    from app.router.stats import router_stat
    app = FastAPI()
    app.state.df = df
    app.include_router(router_stat)
    return app


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def base_df():
    return pd.DataFrame({
        "client_id": [1, 2, 3, 4, 5, 6],
        "amount":    [50.0, 150.0, 600.0, 1500.0, 6000.0, 200.0],
        "is_fraud":  [False, True, False, True, False, False],
        "use_chip":  ["Chip", "Swipe", "Online", "Chip", "Swipe", "Online"],
        "date":      ["2024-01-01", "2024-01-01", "2024-01-02", "2024-01-02", "2024-01-03", "2024-01-03"],
        "errors":    [None, "timeout", None, "invalid_card", None, None],
    })

@pytest.fixture
def empty_df():
    return pd.DataFrame(columns=["client_id", "amount", "is_fraud", "use_chip", "date", "errors"])

@pytest.fixture
def client(base_df):
    return TestClient(make_app(base_df))

@pytest.fixture
def empty_client(empty_df):
    return TestClient(make_app(empty_df))


# ─── GET /api/stats/by-type ───────────────────────────────────────────────────

class TestStatsByTypeRoute:

    def test_status_200(self, client):
        assert client.get("/api/stats/by-type").status_code == 200

    def test_returns_list_of_dicts(self, client):
        result = client.get("/api/stats/by-type").json()
        assert isinstance(result, list)
        assert all(isinstance(r, dict) for r in result)

    def test_correct_keys(self, client):
        result = client.get("/api/stats/by-type").json()
        assert set(result[0].keys()) == {"type", "count", "avg_amount"}

    def test_all_types_present(self, client):
        result = client.get("/api/stats/by-type").json()
        types = {r["type"] for r in result}
        assert types == {"Chip", "Swipe", "Online"}

    def test_empty_dataframe(self, empty_client):
        result = empty_client.get("/api/stats/by-type").json()
        assert result == []

    def test_delegates_to_service(self, base_df):
        mock_return = [{"type": "Chip", "count": 2, "avg_amount": 100.0}]
        with patch("app.router.stats.stats_by_type", return_value=mock_return) as mock:
            result = TestClient(make_app(base_df)).get("/api/stats/by-type").json()
            mock.assert_called_once()
            assert result == mock_return


# ─── GET /api/stats/distribution ─────────────────────────────────────────────

class TestAmountDistributionRoute:

    def test_status_200(self, client):
        assert client.get("/api/stats/distribution").status_code == 200

    def test_returns_bins_and_counts(self, client):
        result = client.get("/api/stats/distribution").json()
        assert "bins" in result
        assert "counts" in result

    def test_counts_sum_to_total(self, client, base_df):
        result = client.get("/api/stats/distribution").json()
        assert sum(result["counts"]) == len(base_df)

    def test_bins_and_counts_same_length(self, client):
        result = client.get("/api/stats/distribution").json()
        assert len(result["bins"]) == len(result["counts"])

    def test_empty_dataframe(self, empty_client):
        result = empty_client.get("/api/stats/distribution").json()
        assert all(c == 0 for c in result["counts"])

    def test_delegates_to_service(self, base_df):
        mock_return = {"bins": ["0-100"], "counts": [3]}
        with patch("app.router.stats.amount_distribution", return_value=mock_return) as mock:
            result = TestClient(make_app(base_df)).get("/api/stats/distribution").json()
            mock.assert_called_once()
            assert result == mock_return


# ─── GET /api/stats/daily ─────────────────────────────────────────────────────

class TestDailyStatsRoute:

    def test_status_200(self, client):
        assert client.get("/api/stats/daily").status_code == 200

    def test_returns_list_of_dicts(self, client):
        result = client.get("/api/stats/daily").json()
        assert isinstance(result, list)
        assert all(isinstance(r, dict) for r in result)

    def test_correct_keys(self, client):
        result = client.get("/api/stats/daily").json()
        assert set(result[0].keys()) == {"date", "volume", "moyenne"}

    def test_date_is_string(self, client):
        result = client.get("/api/stats/daily").json()
        assert all(isinstance(r["date"], str) for r in result)

    def test_aggregation_by_date(self, client):
        result = client.get("/api/stats/daily").json()
        by_date = {r["date"]: r for r in result}
        assert by_date["2024-01-01"]["volume"] == 2
        assert by_date["2024-01-02"]["volume"] == 2

    def test_empty_dataframe(self, empty_client):
        result = empty_client.get("/api/stats/daily").json()
        assert result == []

    def test_delegates_to_service(self, base_df):
        mock_return = [{"date": "2024-01-01", "volume": 2, "moyenne": 100.0}]
        with patch("app.router.stats.obtenir_stats_journalieres_completes", return_value=mock_return) as mock:
            result = TestClient(make_app(base_df)).get("/api/stats/daily").json()
            mock.assert_called_once()
            assert result == mock_return


# ─── GET /api/stats/fraud/summary ────────────────────────────────────────────

class TestFraudSummaryRoute:

    def test_status_200(self, client):
        assert client.get("/api/stats/fraud/summary").status_code == 200

    def test_correct_keys(self, client):
        result = client.get("/api/stats/fraud/summary").json()
        assert set(result.keys()) == {"total_frauds", "flagged", "precision", "recall"}

    def test_500_on_empty_dataframe(self, empty_client):
        response = empty_client.get("/api/stats/fraud/summary")
        assert response.status_code == 500
        assert "vide" in response.json()["detail"].lower()

    def test_500_on_none_df(self, base_df):
        app = make_app(base_df)
        app.state.df = None
        response = TestClient(app).get("/api/stats/fraud/summary")
        assert response.status_code == 500

    def test_404_on_service_error(self, base_df):
        with patch("app.router.stats.calculer_resume_fraude", return_value={"error": "colonne absente"}):
            response = TestClient(make_app(base_df)).get("/api/stats/fraud/summary")
            assert response.status_code == 404
            assert "colonne absente" in response.json()["detail"]

    def test_delegates_to_service(self, base_df):
        mock_return = {"total_frauds": 2, "flagged": 1, "precision": 0.95, "recall": 0.88}
        with patch("app.router.stats.calculer_resume_fraude", return_value=mock_return) as mock:
            result = TestClient(make_app(base_df)).get("/api/stats/fraud/summary").json()
            mock.assert_called_once()
            assert result == mock_return


# ─── GET /api/stats/fraud/by-type ────────────────────────────────────────────

class TestFraudByTypeRoute:

    def test_status_200(self, client):
        assert client.get("/api/stats/fraud/by-type").status_code == 200

    def test_returns_list_of_dicts(self, client):
        result = client.get("/api/stats/fraud/by-type").json()
        assert isinstance(result, list)
        assert all(isinstance(r, dict) for r in result)

    def test_correct_keys(self, client):
        result = client.get("/api/stats/fraud/by-type").json()
        assert set(result[0].keys()) == {"type", "total", "fraud_count", "fraud_rate"}

    def test_fraud_rate_between_0_and_1(self, client):
        result = client.get("/api/stats/fraud/by-type").json()
        for r in result:
            assert 0.0 <= r["fraud_rate"] <= 1.0

    def test_empty_dataframe(self, empty_client):
        result = empty_client.get("/api/stats/fraud/by-type").json()
        assert result == []

    def test_delegates_to_service(self, base_df):
        mock_return = [{"type": "Chip", "total": 2, "fraud_count": 1, "fraud_rate": 0.5}]
        with patch("app.router.stats.calculer_taux_fraude_par_type", return_value=mock_return) as mock:
            result = TestClient(make_app(base_df)).get("/api/stats/fraud/by-type").json()
            mock.assert_called_once()
            assert result == mock_return


# ─── POST /api/stats/fraud/predict ───────────────────────────────────────────

class TestPredictFraudRoute:

    def _payload(self, **kwargs):
        base = {"type": "Chip", "amount": 100.0, "oldbalanceOrg": 1000.0, "newbalanceOrig": 900.0}
        return {**base, **kwargs}

    def test_status_200(self, client):
        response = client.post("/api/stats/fraud/predict", json=self._payload())
        assert response.status_code == 200

    def test_correct_keys(self, client):
        result = client.post("/api/stats/fraud/predict", json=self._payload()).json()
        assert set(result.keys()) == {"isFraud", "probability"}

    def test_is_fraud_is_bool(self, client):
        result = client.post("/api/stats/fraud/predict", json=self._payload()).json()
        assert isinstance(result["isFraud"], bool)

    def test_probability_between_0_and_1(self, client):
        result = client.post("/api/stats/fraud/predict", json=self._payload()).json()
        assert 0.0 <= result["probability"] <= 1.0

    def test_missing_field_returns_422(self, client):
        response = client.post("/api/stats/fraud/predict", json={"type": "Chip", "amount": 100.0})
        assert response.status_code == 422

    def test_invalid_amount_type_returns_422(self, client):
        response = client.post("/api/stats/fraud/predict", json=self._payload(amount="beaucoup"))
        assert response.status_code == 422

    def test_delegates_to_service(self, client):
        mock_return = {"isFraud": True, "probability": 0.87}
        with patch("app.router.stats.simuler_prediction_fraude", return_value=mock_return) as mock:
            result = client.post("/api/stats/fraud/predict", json=self._payload()).json()
            mock.assert_called_once_with(
                type_trans="Chip",
                amount=100.0,
                old_bal=1000.0,
                new_bal=900.0,
            )
            assert result == mock_return

    def test_online_type_higher_probability(self, client):
        chip   = client.post("/api/stats/fraud/predict", json=self._payload(type="Chip")).json()
        online = client.post("/api/stats/fraud/predict", json=self._payload(type="Online")).json()
        assert online["probability"] >= chip["probability"]