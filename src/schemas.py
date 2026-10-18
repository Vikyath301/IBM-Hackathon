"""
Pydantic Schemas & Data Contracts for ChainSentinel Agents and APIs.
Ensures consistent interface across:
- Detection Agent
- Risk Agent
- Recommendation Agent
- Explanation Agent
- LangGraph Workflow
- FastAPI Endpoints
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class TransactionInput(BaseModel):
    order_id: int = Field(default=88410, description="Order ID from Db2 for z/OS")
    product_name: str = Field(default="Semiconductor MCU-8", description="Item SKU / Name")
    category_name: str = Field(default="Electronics", description="Product Category")
    shipping_mode: str = Field(default="Standard Class", description="Mode: Standard, Second, First, Same Day")
    customer_country: str = Field(default="EE. UU.", description="Origin / Customer Country")
    order_country: str = Field(default="France", description="Destination Country")
    order_region: str = Field(default="Western Europe", description="Destination Region")
    scheduled_days: int = Field(default=4, description="Contractual shipping SLA days")
    order_item_quantity: int = Field(default=5, description="Item quantity")
    order_value: float = Field(default=2450.00, description="Total order amount ($)")

class AnomalyDetectionResult(BaseModel):
    is_anomaly: bool = Field(description="Flag indicating unusual transaction characteristics")
    anomaly_score: float = Field(description="Normalized anomaly score between 0.0 and 1.0")
    anomaly_reasons: List[str] = Field(default_factory=list, description="Specific triggers or suspicious factors")

class RiskDriver(BaseModel):
    feature: str = Field(description="Feature or factor name")
    impact_pct: float = Field(description="Percentage contribution to the risk score")
    direction: str = Field(default="INCREASES_RISK", description="INCREASES_RISK or REDUCES_RISK")
    description: str = Field(default="", description="Contextual description of why this feature drives risk")

class RiskAssessmentResult(BaseModel):
    late_delivery_probability: float = Field(description="ML-predicted delay probability [0.0 - 1.0]")
    is_high_risk: bool = Field(description="Binary threshold flag (probability >= 0.5)")
    alert_level: str = Field(description="NORMAL, WARNING, or CRITICAL")
    dollar_at_risk: float = Field(description="Financial exposure calculated from risk probability")
    fastest_predicted_days: int = Field(description="Predicted expedited arrival days")
    normal_predicted_days: int = Field(description="Predicted standard arrival days")
    primary_risk_factors: List[str] = Field(default_factory=list, description="Key features driving the risk prediction")
    risk_drivers: List[RiskDriver] = Field(default_factory=list, description="SHAP feature attribution breakdown")

class ActionOption(BaseModel):
    rank: int
    action: str
    title: str
    feasibility: str
    estimated_expedite_cost: float
    protected_revenue: float
    roi_ratio: Optional[str] = "24.5x"
    turnaround_days: Optional[int] = 2
    simulation_notes: str = Field(default="Estimated based on historical carrier rates and inventory hub buffers")

class RecommendationResult(BaseModel):
    recommended_actions: List[ActionOption] = Field(default_factory=list)
    top_action: Optional[ActionOption] = None

class ExplanationResult(BaseModel):
    executive_summary: str
    technical_justification: str
    model_source: str = Field(default="IBM Granite Foundation Model (s390x)")

class DisruptionAnalysisResponse(BaseModel):
    order_id: int
    product_name: str
    category_name: str
    customer_country: str = Field(default="EE. UU.", description="Origin Country")
    order_country: str
    shipping_mode: str
    scheduled_days: int = Field(default=4, description="Contractual shipping SLA days")
    order_value: float
    detection: AnomalyDetectionResult
    risk: RiskAssessmentResult
    recommendations: List[ActionOption]
    explanation: str
    latency_ms: float
    pipeline_status: str = Field(default="SUCCESS")
