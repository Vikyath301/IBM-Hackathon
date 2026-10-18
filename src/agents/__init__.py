"""
ChainSentinel Multi-Agent Package.
Modules:
- detection_agent: Anomaly and outlier pattern detector
- risk_agent: Machine-learning disruption & duration scoring
- recommendation_agent: Prescriptive action ranking
- explanation_agent: Natural language executive justification
"""
from .detection_agent import DetectionAgent
from .risk_agent import RiskAgent
from .recommendation_agent import RecommendationAgent
from .explanation_agent import ExplanationAgent

__all__ = [
    "DetectionAgent",
    "RiskAgent",
    "RecommendationAgent",
    "ExplanationAgent"
]
