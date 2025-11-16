from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_latest_endpoint():
    response = client.get("/api/v1/ohlcv/latest?symbol=BINANCE:SOLUSDT.P")
    assert response.status_code in (200, 404)
