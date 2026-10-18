"""
Detection Agent (Member 3).
Identifies unusual order patterns, lead-time variances, and operational anomalies
prior to ML risk scoring.
"""
from typing import Dict, Any, List
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from schemas import TransactionInput, AnomalyDetectionResult

class DetectionAgent:
    def __init__(self, high_value_threshold: float = 3000.0):
        self.high_value_threshold = high_value_threshold

    def analyze(self, txn: TransactionInput) -> AnomalyDetectionResult:
        reasons = []
        score = 0.0

        # Check 1: Cross-border friction on standard SLA
        is_international = txn.customer_country != txn.order_country
        if is_international and txn.shipping_mode == "Standard Class":
            reasons.append(f"Cross-border transit ({txn.customer_country} -> {txn.order_country}) assigned to lowest-tier Ground carrier.")
            score += 0.35

        # Check 2: Unusually high order value
        if txn.order_value >= self.high_value_threshold:
            reasons.append(f"High-value transaction (${txn.order_value:,.2f}) exceeding standard buffer threshold (${self.high_value_threshold:,.2f}).")
            score += 0.30

        # Check 3: Tight SLA vs Ground shipping mode
        if txn.scheduled_days <= 2 and txn.shipping_mode in ["Standard Class", "Second Class"]:
            reasons.append(f"Compressed SLA ({txn.scheduled_days} days) incompatible with {txn.shipping_mode} transit guarantees.")
            score += 0.25

        # Check 4: Bulk unit quantities
        if txn.order_item_quantity >= 50:
            reasons.append(f"Large bulk volume ({txn.order_item_quantity} units) risking warehouse fulfillment bottlenecks.")
            score += 0.20

        normalized_score = min(1.0, round(score, 2))
        is_anomaly = normalized_score >= 0.40

        return AnomalyDetectionResult(
            is_anomaly=is_anomaly,
            anomaly_score=normalized_score,
            anomaly_reasons=reasons if reasons else ["Transaction characteristics align with standard operational baselines."]
        )
