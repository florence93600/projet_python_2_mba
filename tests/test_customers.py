import pytest
import pandas as pd
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch


# ─── App factory ─────────────────────────────────────────────────────────────

def make_app(df: pd.DataFrame) -> FastAPI:
    from app.router.customer import router_customers
    app = FastAPI()
    app.state.df = df
    app.include_router(router_customers)
    return app


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def base_df():
    return pd.DataFrame({
        "client_id": [1, 1, 2, 3, 3, 3, None],
        "amount":    [100.0, 200.0, 50.0, 300.0, 150.0, 50.0, 999.0],
        "is_fraud":  [False, False, True, False, True, False, False],
        "use_chip":  ["Chip", "Chip", "Swipe", "Online", "Chip", "Swipe", "Online"],
    })

@pytest.fixture
def empty_df():
    return pd.DataFrame(columns=["client_id", "amount", "is_fraud", "use_chip"])

@pytest.fixture
def client(base_df):
    return TestClient(make_app(base_df))

@pytest.fixture
def empty_client(empty_df):
    return TestClient(make_app(empty_df))


class TestListCustomersRoute:

    def test_status_200(self, client):
        response = client.get("/api/customers")
        assert response.status_code == 200

    def test_returns_list_of_strings(self, client):
        result = client.get("/api/customers").json()
        assert isinstance(result, list)
        assert all(isinstance(c, str) for c in result)

    def test_sorted_and_deduplicated(self, client):
        result = client.get("/api/customers").json()
        assert result == sorted(set(result))

    def test_excludes_null(self, client):
        result = client.get("/api/customers").json()
        assert "nan" not in result
        assert None not in result

    def test_empty_dataframe(self, empty_client):
        result = empty_client.get("/api/customers").json()
        assert result == []

    def test_delegates_to_service(self, base_df):
        with patch("app.router.customer.list_customers", return_value=["1", "2"]) as mock:
            client = TestClient(make_app(base_df))
            response = client.get("/api/customers")
            mock.assert_called_once()
            assert response.json() == ["1", "2"]



class TestTopCustomersRoute:

    def test_status_200(self, client):
        response = client.get("/api/customers/top")
        assert response.status_code == 200

    def test_returns_list_of_dicts(self, client):
        result = client.get("/api/customers/top").json()
        assert isinstance(result, list)
        assert all(isinstance(r, dict) for r in result)

    def test_correct_keys(self, client):
        result = client.get("/api/customers/top").json()
        assert set(result[0].keys()) == {"customer_id", "total_amount"}

    def test_default_n_is_10(self, client):
        result = client.get("/api/customers/top").json()
        assert len(result) <= 10

    def test_n_query_param(self, client):
        result = client.get("/api/customers/top?n=2").json()
        assert len(result) == 2

    def test_n_1_returns_single_item(self, client):
        result = client.get("/api/customers/top?n=1").json()
        assert len(result) == 1

    def test_sorted_descending(self, client):
        result = client.get("/api/customers/top").json()
        amounts = [r["total_amount"] for r in result]
        assert amounts == sorted(amounts, reverse=True)

    def test_n_zero_returns_422(self, client):
        response = client.get("/api/customers/top?n=0")
        assert response.status_code == 422

    def test_n_negative_returns_422(self, client):
        response = client.get("/api/customers/top?n=-5")
        assert response.status_code == 422

    def test_n_string_returns_422(self, client):
        response = client.get("/api/customers/top?n=abc")
        assert response.status_code == 422

    def test_empty_dataframe(self, empty_client):
        result = empty_client.get("/api/customers/top").json()
        assert result == []

    def test_delegates_to_service(self, base_df):
        mock_return = [{"customer_id": "1", "total_amount": 300.0}]
        with patch("app.router.customer.top_customers", return_value=mock_return) as mock:
            client = TestClient(make_app(base_df))
            response = client.get("/api/customers/top?n=5")
            mock.assert_called_once()
            _, kwargs = mock.call_args
            assert kwargs.get("n") == 5
            assert response.json() == mock_return