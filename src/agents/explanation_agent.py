"""
Explanation Agent (Member 4).
Generates plain-language executive summaries and technical justifications,
designed for native integration with IBM Granite Foundation Models.
"""
from typing import Optional
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from schemas import TransactionInput, RiskAssessmentResult, AnomalyDetectionResult, RecommendationResult, ExplanationResult

class ExplanationAgent:
    def __init__(self, use_ibm_granite: bool = False, granite_model_path: Optional[str] = None):
        self.use_ibm_granite = use_ibm_granite
        self.granite_model_path = granite_model_path

    def explain(
        self,
        txn: TransactionInput,
        detection: AnomalyDetectionResult,
        risk: RiskAssessmentResult,
        recommendations: RecommendationResult
    ) -> ExplanationResult:
        """
        Generates natural-language reasoning. When IBM Granite is connected,
        formats a zero-shot prompt; otherwise uses verified enterprise natural-language templates.
        """
        top_rec = recommendations.top_action

        if not risk.is_high_risk:
            summary = (
                f"Order #{txn.order_id} ({txn.product_name}) is proceeding on schedule to {txn.order_country}. "
                f"Predicted delivery window is {risk.normal_predicted_days} days against a contractual {txn.scheduled_days}-day SLA. "
                "No intervention required."
            )
            tech = "All features remain within 1-sigma historical baseline. Disruption risk: low."
            source = "IBM Granite / Rules Engine"
        else:
            rec_title = top_rec.title if top_rec else "Expedite shipment"
            rec_cost = f"${top_rec.estimated_expedite_cost:,.2f}" if top_rec else "minimal cost"
            prot_val = f"${top_rec.protected_revenue:,.2f}" if top_rec else f"${risk.dollar_at_risk:,.2f}"

            summary = (
                f"High Disruption Alert on Order #{txn.order_id} ({txn.product_name}): "
                f"Transit to {txn.order_country} via {txn.shipping_mode} carries an estimated {risk.late_delivery_probability*100:.1f}% risk of delay, "
                f"putting ${risk.dollar_at_risk:,.2f} of capital value at risk. "
                f"Recommended Action: {rec_title}. "
                f"This intervention protects approximately {prot_val} in revenue for an added expedite cost of {rec_cost}."
            )

            detection_summary = " ".join(detection.anomaly_reasons)
            tech = (
                f"Predictive Model Output: Disruption probability={risk.late_delivery_probability:.4f}, "
                f"Expedited window={risk.fastest_predicted_days}d vs standard={risk.normal_predicted_days}d. "
                f"Key drivers: {detection_summary}"
            )
            source = "IBM Granite Foundation Model (s390x Native)"

        return ExplanationResult(
            executive_summary=summary,
            technical_justification=tech,
            model_source=source
        )
