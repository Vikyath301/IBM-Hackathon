"""
Risk Agent (Member 2/3).
Executes the trained Machine Learning pipeline to score disruption probability,
estimate delivery duration ranges, and calculate Dollar-at-Risk financial exposure.
"""
import sys
import os
from typing import Dict, Any, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from predict_risk import DisruptionPredictor
from schemas import TransactionInput, RiskAssessmentResult

class RiskAgent:
    def __init__(self, models_dir: str = None):
        self.predictor = DisruptionPredictor(models_dir=models_dir)

    def evaluate(self, txn: TransactionInput) -> RiskAssessmentResult:
        event_dict = {
            "Order Id": txn.order_id,
            "Product Name": txn.product_name,
            "Category Name": txn.category_name,
            "Shipping Mode": txn.shipping_mode,
            "Customer Country": txn.customer_country,
            "Order Country": txn.order_country,
            "Order Region": txn.order_region,
            "Days for shipment (scheduled)": txn.scheduled_days,
            "Order Item Quantity": txn.order_item_quantity,
            "Sales": txn.order_value,
            "Order Item Total": txn.order_value
        }

        # Run trained ML models (Classifier + Regressor)
        ml_output = self.predictor.predict_event(event_dict)

        # Factor attribution
        factors = []
        if ml_output["late_delivery_probability"] >= 0.50:
            factors.append(f"Carrier Mode: {txn.shipping_mode} historically exhibits elevated variance on route {txn.order_region}.")
            if txn.customer_country != txn.order_country:
                factors.append(f"International customs and clearance delays associated with {txn.order_country}.")
            if txn.order_value > 2000:
                factors.append("High capital value exposure requires priority carrier allocation.")
        else:
            factors.append("Order parameters match standard predictable fulfillment distributions.")

        return RiskAssessmentResult(
            late_delivery_probability=ml_output["late_delivery_probability"],
            is_high_risk=ml_output["is_high_risk"],
            alert_level=ml_output["alert_level"],
            dollar_at_risk=ml_output["dollar_at_risk"],
            fastest_predicted_days=ml_output["fastest_predicted_days"],
            normal_predicted_days=ml_output["normal_predicted_days"],
            primary_risk_factors=factors
        )
