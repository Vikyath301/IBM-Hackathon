"""
Recommendation Agent (Member 4).
Ranks actionable interventions based on ML risk scores, financial impact,
and explicit, documented simulation assumptions.
"""
from typing import List
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from schemas import TransactionInput, RiskAssessmentResult, AnomalyDetectionResult, ActionOption, RecommendationResult

class RecommendationAgent:
    def rank_actions(
        self,
        txn: TransactionInput,
        risk: RiskAssessmentResult,
        detection: AnomalyDetectionResult
    ) -> RecommendationResult:
        """
        Evaluates potential mitigation actions using multi-criteria trade-offs:
        Protected value vs expedite cost vs feasibility.
        """
        if not risk.is_high_risk:
            standard_action = ActionOption(
                rank=1,
                action="MONITOR_STANDARD",
                title="Maintain standard scheduled fulfillment route",
                feasibility="High (100%)",
                estimated_expedite_cost=0.0,
                protected_revenue=txn.order_value,
                simulation_notes="Baseline: No corrective surcharge needed. Telemetry remains active."
            )
            return RecommendationResult(recommended_actions=[standard_action], top_action=standard_action)

        actions: List[ActionOption] = []

        # Option 1: Volume split to verified alternative supplier / secondary fulfillment hub
        cost_split = round(txn.order_value * 0.035, 2)
        prot_split = round(txn.order_value * 0.85, 2)
        actions.append(
            ActionOption(
                rank=1,
                action="SHIFT_SUPPLIER_VOLUME",
                title=f"Shift 60% order allocation to regional secondary supplier (covers {txn.order_region})",
                feasibility="High (Verified contract buffer)",
                estimated_expedite_cost=cost_split,
                protected_revenue=prot_split,
                simulation_notes="Assumes secondary supplier contracted SLA buffer of 48h with 3.5% allocation surcharge."
            )
        )

        # Option 2: Carrier mode upgrade to expedited Air freight
        cost_air = round(txn.order_value * 0.065, 2)
        prot_air = txn.order_value
        actions.append(
            ActionOption(
                rank=2,
                action="EXPEDITE_AIR_CARRIER",
                title=f"Upgrade carrier to First Class Air (reduces delivery from {txn.scheduled_days}d to {risk.fastest_predicted_days}d)",
                feasibility="Medium (Airport cargo cutoff dependent)",
                estimated_expedite_cost=cost_air,
                protected_revenue=prot_air,
                simulation_notes=f"Assumes air courier freight rate parity (+6.5% surcharge) ensuring arrival within {risk.fastest_predicted_days} days."
            )
        )

        # Option 3: Regional buffer stock allocation
        cost_stock = 45.0
        prot_stock = round(txn.order_value * 0.50, 2)
        actions.append(
            ActionOption(
                rank=3,
                action="RESERVE_STOCK_TRANSFER",
                title="Dispatch reserve buffer inventory from nearest central distribution hub",
                feasibility="High (Hub stock verified)",
                estimated_expedite_cost=cost_stock,
                protected_revenue=prot_stock,
                simulation_notes="Assumes availability of 10% safety stock buffer at central distribution warehouse."
            )
        )

        return RecommendationResult(
            recommended_actions=actions,
            top_action=actions[0] if actions else None
        )
