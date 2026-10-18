"""
Integration Tests for FastAPI & LangGraph Multi-Agent Backend.
Validates:
- GET /health
- POST /analyze (LangGraph workflow)
- POST /simulate-disruption
- POST /api/zos-connect/execute
"""
import sys
import os
from fastapi.testclient import TestClient

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from server import app

client = TestClient(app)

def test_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "agents" in data

def test_analyze_endpoint_langgraph():
    payload = {
        "order_id": 88410,
        "product_name": "High Performance Microcontroller",
        "category_name": "Electronics",
        "shipping_mode": "Standard Class",
        "customer_country": "EE. UU.",
        "order_country": "France",
        "order_region": "Western Europe",
        "scheduled_days": 4,
        "order_item_quantity": 10,
        "order_value": 4500.00
    }
    resp = client.post("/analyze", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "detection" in data
    assert "risk" in data
    assert "recommendations" in data
    assert "explanation" in data
    assert len(data["recommendations"]) > 0
    assert "risk_drivers" in data["risk"]
    assert len(data["risk"]["risk_drivers"]) > 0

def test_simulate_disruption_endpoint():
    resp = client.post("/simulate-disruption")
    assert resp.status_code == 200
    data = resp.json()
    assert data["order_id"] == 4471
    assert data["risk"]["late_delivery_probability"] == 0.87
    assert data["risk"]["alert_level"] == "CRITICAL"
    assert "risk_drivers" in data["risk"]
    assert len(data["risk"]["risk_drivers"]) == 5

def test_zos_connect_execute():
    payload = {
        "order_id": 4471,
        "action_type": "SHIFT_SUPPLIER_VOLUME",
        "selected_recommendation": "Shift 60% of volume to Supplier B",
        "operator_notes": "Test Operator"
    }
    resp = client.post("/api/zos-connect/execute", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "SUCCESS"
    assert data["db2_return_code"] == "0000 (SUCCESS_COMMIT)"

def test_audit_report_endpoint():
    resp = client.get("/api/audit-report/4471")
    assert resp.status_code == 200
    data = resp.json()
    assert data["report_id"] == "CSR-2026-4471"
    assert "mainframe_audit_trail" in data
    assert data["mainframe_audit_trail"]["db2_return_code"] == "0000 (SUCCESS_COMMIT)"
    assert data["mainframe_audit_trail"]["security_hash"].startswith("SHA256:")

if __name__ == "__main__":
    test_health_endpoint()
    test_analyze_endpoint_langgraph()
    test_simulate_disruption_endpoint()
    test_zos_connect_execute()
    test_audit_report_endpoint()
    print("ALL API & LANGGRAPH TESTS PASSED!")
