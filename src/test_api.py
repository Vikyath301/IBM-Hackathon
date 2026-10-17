"""
Test script for Member 2's FastAPI & z/OS Connect Backend.
Demonstrates calling the API endpoints programmatically.
"""
import json
import urllib.request

BASE_URL = "http://127.0.0.1:8000"

def test_backend_flow():
    print("=====================================================")
    print("   ChainSentinel: Testing Backend API & z/OS Connect ")
    print("=====================================================\n")

    # 1. Health check
    print("1. Checking System Health...")
    req = urllib.request.Request(f"{BASE_URL}/api/health")
    with urllib.request.urlopen(req) as resp:
        health_data = json.loads(resp.read().decode())
        print(f"   [Status]: {health_data['status'].upper()}")
        print(f"   [Platform]: {health_data['platform']}")
        print(f"   [z/OS Gateway]: {health_data['zos_connect_gateway']}\n")

    # 2. Evaluate Disruption
    print("2. Sending Transaction to AI Analytics Layer (T+0s -> T+4s)...")
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
    req = urllib.request.Request(
        f"{BASE_URL}/api/evaluate",
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req) as resp:
        eval_result = json.loads(resp.read().decode())
        print(f"   [Disruption Risk]: {eval_result['late_delivery_probability']*100:.1f}%")
        print(f"   [Alert Level]:     {eval_result['alert_level']}")
        print(f"   [Dollar at Risk]:  ${eval_result['dollar_at_risk']:,.2f}")
        print(f"   [Fastest Window]:  {eval_result['fastest_predicted_days']} days (Scheduled: {eval_result['scheduled_days']} days)")
        print(f"   [GenAI Explainer]: {eval_result['genai_explanation']}")
        print(f"   [Top Action]:      {eval_result['recommendations'][0]['title']}\n")

    # 3. Simulate z/OS Connect API Closed Loop (T+5s)
    print("3. Invoking z/OS Connect REST API to commit action to IBM Z...")
    action_payload = {
        "order_id": 88410,
        "action_type": "SHIFT_VOLUME",
        "selected_recommendation": eval_result['recommendations'][0]['title'],
        "operator_notes": "Operations Manager Approved via ChainSentinel Dashboard"
    }
    req = urllib.request.Request(
        f"{BASE_URL}/api/zos-connect/execute",
        data=json.dumps(action_payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req) as resp:
        commit_result = json.loads(resp.read().decode())
        print(f"   [z/OS Commit Status]:   {commit_result['status']}")
        print(f"   [Transaction ID]:       {commit_result['zos_connect_transaction_id']}")
        print(f"   [Db2 Return Code]:      {commit_result['db2_return_code']}")
        print(f"   [Mainframe Audit Log]:  {commit_result['mainframe_audit_log']}\n")

    print("SUCCESS: End-to-end backend & IBM Z loop validated!")

if __name__ == '__main__':
    test_backend_flow()
