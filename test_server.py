"""
Test FastAPI TMA Sync Server
"""
import sys
import asyncio

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_api():
    # 1. Health check
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"
    print("✓ /api/health OK")

    # 2. Static files
    res = client.get("/")
    assert res.status_code == 200
    assert "Money Tracker" in res.text
    print("✓ GET / (index.html) OK")

    res = client.get("/sw.js")
    assert res.status_code == 200
    assert "money-tracker-" in res.text
    print("✓ GET /sw.js OK")

    res = client.get("/manifest.json")
    assert res.status_code == 200
    print("✓ GET /manifest.json OK")

    # 3. Sync offline transaction
    payload = {
        "userId": "123456789",
        "transaction": {
            "id": "local_temp_001",
            "type": "expense",
            "category": "Food",
            "amount": 25.50,
            "currency": "USD",
            "wallet": "Bank",
            "note": "Team dinner",
            "date": "2026-10-19T12:00:00Z"
        }
    }
    res = client.post("/api/sync", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "server_id" in data
    print(f"✓ POST /api/sync OK (server_id: {data['server_id']})")

    # 4. Fetch transactions
    res = client.get("/api/transactions?userId=123456789")
    assert res.status_code == 200
    tx_data = res.json()
    assert len(tx_data["transactions"]) >= 1
    print(f"✓ GET /api/transactions OK (retrieved {len(tx_data['transactions'])} records)")

    # 5. Categories endpoints
    res = client.get("/api/categories?userId=123456789")
    assert res.status_code == 200
    cats = res.json()
    assert "Food" in cats["expense"]
    assert "Salary" in cats["income"]
    print("✓ GET /api/categories OK")

    cat_payload = {
        "userId": "123456789",
        "type": "expense",
        "name": "Gym"
    }
    res = client.post("/api/categories", json=cat_payload)
    assert res.status_code == 200
    cat_res = res.json()
    assert cat_res["status"] == "success"
    assert "Gym" in cat_res["categories"]
    print("✓ POST /api/categories OK (added custom category 'Gym')")

    # 6. Telegram webhook endpoints
    res = client.get("/api/telegram-info")
    assert res.status_code == 200
    print("✓ GET /api/telegram-info OK")

    res = client.post("/api/telegram-webhook", json={"update_id": 999999})
    assert res.status_code == 200
    print("✓ POST /api/telegram-webhook OK")

    print("\n🎉 ALL SERVER API TESTS PASSED!")

if __name__ == "__main__":
    test_api()
