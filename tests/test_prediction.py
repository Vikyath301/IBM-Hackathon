"""
Unit Tests for Machine Learning Prediction Pipeline.
Validates:
- Model loading
- Output probability bounds [0.0 - 1.0]
- Durations non-negative
- Dollar-at-risk calculation
"""
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from predict_risk import DisruptionPredictor

def test_prediction_output_bounds():
    predictor = DisruptionPredictor()
    test_event = {
        "Order Id": 1001,
        "Product Name": "Diagnostic Controller",
        "Category Name": "Electronics",
        "Shipping Mode": "Standard Class",
        "Customer Country": "EE. UU.",
        "Order Country": "France",
        "Order Region": "Western Europe",
        "Days for shipment (scheduled)": 4,
        "Order Item Quantity": 2,
        "Sales": 500.00
    }
    result = predictor.predict_event(test_event)
    
    assert 0.0 <= result["late_delivery_probability"] <= 1.0
    assert result["fastest_predicted_days"] >= 0
    assert result["normal_predicted_days"] >= result["fastest_predicted_days"]
    assert result["dollar_at_risk"] == round(result["late_delivery_probability"] * 500.00, 2)
    assert result["alert_level"] in ["NORMAL", "WARNING", "CRITICAL"]

def test_zero_leakage_columns_not_required():
    predictor = DisruptionPredictor()
    # Ensure predictor does NOT fail when post-delivery leakage columns are absent
    clean_event = {
        "Order Id": 1002,
        "Product Name": "Sports Cleats",
        "Category Name": "Footwear",
        "Shipping Mode": "First Class",
        "Customer Country": "EE. UU.",
        "Order Country": "EE. UU.",
        "Order Region": "North America",
        "Days for shipment (scheduled)": 1,
        "Order Item Quantity": 1,
        "Sales": 120.00
    }
    result = predictor.predict_event(clean_event)
    assert result["order_id"] == 1002
    assert "late_delivery_probability" in result

if __name__ == "__main__":
    test_prediction_output_bounds()
    test_zero_leakage_columns_not_required()
    print("ALL PREDICTION TESTS PASSED!")
