"""
LangGraph Multi-Agent Workflow Orchestrator.
Coordinates:
1. Detection Agent (Anomaly triage)
2. Risk Agent (ML inference)
3. Recommendation Agent (Prescriptive ranking)
4. Explanation Agent (IBM Granite explanation)
5. LangSmith Observability & Tracing
"""
import os
import time
from typing import TypedDict, Optional
from dotenv import load_dotenv

# Load LangSmith and environmental configurations
load_dotenv()

from langgraph.graph import StateGraph, START, END

from schemas import (
    TransactionInput,
    AnomalyDetectionResult,
    RiskAssessmentResult,
    RecommendationResult,
    ExplanationResult,
    DisruptionAnalysisResponse
)
from agents.detection_agent import DetectionAgent
from agents.risk_agent import RiskAgent
from agents.recommendation_agent import RecommendationAgent
from agents.explanation_agent import ExplanationAgent

# 1. Define State Contract
class WorkflowState(TypedDict):
    transaction: TransactionInput
    start_time: float
    detection: Optional[AnomalyDetectionResult]
    risk: Optional[RiskAssessmentResult]
    recommendations: Optional[RecommendationResult]
    explanation: Optional[ExplanationResult]
    final_response: Optional[DisruptionAnalysisResponse]

# 2. Instantiate Agents
detection_agent = DetectionAgent()
risk_agent = RiskAgent()
recommendation_agent = RecommendationAgent()
explanation_agent = ExplanationAgent()

# 3. Node Functions
def detection_node(state: WorkflowState) -> dict:
    result = detection_agent.analyze(state["transaction"])
    return {"detection": result}

def risk_node(state: WorkflowState) -> dict:
    result = risk_agent.evaluate(state["transaction"])
    return {"risk": result}

def recommendation_node(state: WorkflowState) -> dict:
    result = recommendation_agent.rank_actions(
        txn=state["transaction"],
        risk=state["risk"],
        detection=state["detection"]
    )
    return {"recommendations": result}

def explanation_node(state: WorkflowState) -> dict:
    result = explanation_agent.explain(
        txn=state["transaction"],
        detection=state["detection"],
        risk=state["risk"],
        recommendations=state["recommendations"]
    )
    return {"explanation": result}

def response_assembly_node(state: WorkflowState) -> dict:
    txn = state["transaction"]
    detection = state["detection"]
    risk = state["risk"]
    recs = state["recommendations"]
    exp = state["explanation"]
    latency = round((time.time() - state["start_time"]) * 1000, 2)

    response = DisruptionAnalysisResponse(
        order_id=txn.order_id,
        product_name=txn.product_name,
        category_name=txn.category_name,
        order_country=txn.order_country,
        shipping_mode=txn.shipping_mode,
        order_value=txn.order_value,
        detection=detection,
        risk=risk,
        recommendations=recs.recommended_actions,
        explanation=exp.executive_summary,
        latency_ms=latency,
        pipeline_status="SUCCESS"
    )
    return {"final_response": response}

# 4. Build State Graph
graph_builder = StateGraph(WorkflowState)

graph_builder.add_node("detection", detection_node)
graph_builder.add_node("risk", risk_node)
graph_builder.add_node("recommendation", recommendation_node)
graph_builder.add_node("explanation", explanation_node)
graph_builder.add_node("assembly", response_assembly_node)

# Flow: START -> Detection -> Risk -> Recommendation -> Explanation -> Assembly -> END
graph_builder.add_edge(START, "detection")
graph_builder.add_edge("detection", "risk")
graph_builder.add_edge("risk", "recommendation")
graph_builder.add_edge("recommendation", "explanation")
graph_builder.add_edge("explanation", "assembly")
graph_builder.add_edge("assembly", END)

workflow = graph_builder.compile()

def run_workflow(txn: TransactionInput) -> DisruptionAnalysisResponse:
    """Executes the full LangGraph multi-agent pipeline."""
    initial_state: WorkflowState = {
        "transaction": txn,
        "start_time": time.time(),
        "detection": None,
        "risk": None,
        "recommendations": None,
        "explanation": None,
        "final_response": None
    }
    result_state = workflow.invoke(initial_state)
    return result_state["final_response"]

if __name__ == "__main__":
    test_txn = TransactionInput(
        order_id=4471,
        product_name="Tier-1 Enterprise Server Modules",
        category_name="Electronics",
        shipping_mode="Standard Class",
        customer_country="EE. UU.",
        order_country="France",
        order_region="Western Europe",
        scheduled_days=4,
        order_item_quantity=800,
        order_value=1900000.00
    )
    res = run_workflow(test_txn)
    print("\n--- LangGraph Multi-Agent Workflow Result ---")
    print(f"Order: #{res.order_id} ({res.product_name})")
    print(f"Anomaly Detected: {res.detection.is_anomaly} (Score: {res.detection.anomaly_score})")
    print(f"Disruption Risk: {res.risk.late_delivery_probability*100:.1f}% ({res.risk.alert_level})")
    print(f"Dollar at Risk: ${res.risk.dollar_at_risk:,.2f}")
    print(f"Top Action: {res.recommendations[0].title}")
    print(f"Explanation: {res.explanation}")
    print(f"Latency: {res.latency_ms} ms")
