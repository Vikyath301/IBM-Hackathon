# 🛡️ ChainSentinel: Master Team & Architecture Guide
**Team PingXero | IBM Z Datathon**

This document contains the complete architectural specification, multi-agent implementation, and testing workflows for **ChainSentinel**. Any team member or AI assistant can use this guide to understand the system, run the code, and extend the platform.

---

## 📌 1. Project Overview & Philosophy
* **Tagline:** Real-time predictive supply chain disruption intelligence with GenAI explanations, built on IBM Z.
* **Core Philosophy:** **Do not build five separate ML models just to label them agents.** We train a single robust machine learning pipeline for the prediction task, engineer four specialized agents for distinct operational responsibilities, and coordinate them using **LangGraph** with **LangSmith** tracing.
* **The 4-Stage Flywheel:**
  1. **Detection Agent (`src/agents/detection_agent.py`):** Flags anomalous transactions, compressed SLAs, and cross-border route friction.
  2. **Risk Agent (`src/agents/risk_agent.py`):** Calls the trained ML model (`models/risk_classifier.joblib`), scoring disruption probabilities, delivery duration windows, and financial Dollar-at-Risk.
  3. **Recommendation Agent (`src/agents/recommendation_agent.py`):** Ranks feasible mitigation interventions (carrier expedite, volume shift, safety buffer) based on explicit, documented trade-offs.
  4. **Explanation Agent (`src/agents/explanation_agent.py`):** Synthesizes natural-language executive rationales (formatted for IBM Granite on s390x).
  5. **Closed Loop:** Commits approved actions back to core systems via **z/OS Connect REST APIs** (`RC=0000 SUCCESS_COMMIT`).

---

## 📁 2. Repository Structure
```
chainsentinel/
├── data/
│   ├── dataco_sample.csv               # 5,000 supply chain transaction records
│   ├── clients.csv                     # (IBM LinuxONE environment dataset)
│   ├── transaction_history.csv         # (IBM LinuxONE environment dataset)
│   └── transactions.csv                # (IBM LinuxONE environment dataset)
│
├── models/
│   ├── risk_classifier.joblib          # Trained ML Disruption Risk Classifier
│   ├── duration_regressor.joblib       # Multi-Output Shipping Duration Regressor
│   └── preprocessor.joblib             # ColumnTransformer (OneHot + StandardScaler)
│
├── src/
│   ├── data_pipeline.py                # Zero-leakage preprocessing & feature engineering
│   ├── train_models.py                 # Model training & metric evaluation
│   ├── predict_risk.py                 # Low-latency ML inference module (~11ms)
│   ├── stream_simulator.py             # IBM Z / Db2 transaction stream generator
│   ├── server.py                       # FastAPI entry point exposing /analyze, /alerts, etc.
│   ├── schemas.py                      # Pydantic data contracts for agents and APIs
│   ├── workflow.py                     # LangGraph state graph coordinating all 4 agents
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── detection_agent.py          # Operational anomaly detector
│   │   ├── risk_agent.py               # ML risk & duration scoring agent
│   │   ├── recommendation_agent.py     # Prescriptive action ranking agent
│   │   └── explanation_agent.py        # IBM Granite executive explanation agent
│   └── static/
│       └── index.html                  # Real-time command center dashboard
│
├── tests/
│   ├── test_prediction.py              # Unit tests for ML predictions & bounds
│   └── test_api.py                     # Integration tests for LangGraph & FastAPI
│
├── ChainSentinel_IBM_Z_Demo.ipynb     # Self-contained IBM LinuxONE demo notebook
├── requirements.txt                    # Project dependencies
├── .env.example                        # Template for LangSmith & Watsonx secrets
├── .env                                # Local secrets (git-ignored)
├── .gitignore
├── README.md
└── TEAM_GUIDE.md
```

---

## 👥 3. 6-Member Team Role Division

| Teammate | Assigned Responsibility | Primary Code Modules |
| :--- | :--- | :--- |
| **Member 1 (Data Engineering)** | Dataset inspection, schema cleaning, zero-leakage validation | `src/data_pipeline.py`, `data/` |
| **Member 2 (ML Prediction)** | Train, evaluate, and serialize models; inference logic | `src/train_models.py`, `src/predict_risk.py`, `models/` |
| **Member 3 (Detection Agent)** | Anomaly detection, compressed SLA flags, risk evidence | `src/agents/detection_agent.py` |
| **Member 4 (Recommendations & Explanations)** | Action ranking, cost trade-offs, IBM Granite explanations | `src/agents/recommendation_agent.py`, `src/agents/explanation_agent.py` |
| **Member 5 (Backend & LangGraph)** | FastAPI server, LangGraph state graph, LangSmith tracing | `src/server.py`, `src/workflow.py`, `src/schemas.py`, `tests/` |
| **Member 6 (Frontend & Live Demo)** | Command center UI, live ticker, Slide 8 disruption demo | `src/static/index.html`, PPT Slide Deck |

---

## 🔍 4. LinuxONE Dataset Inspection Script

When working inside your **IBM LinuxONE JupyterLab instance** (`http://148.100.109.180:38888/tree?`), run this cell to inspect the CSV files:

```python
import pandas as pd
from pathlib import Path

data_dir = Path("data")
files = [
    "clients.csv",
    "dataco_sample.csv",
    "transaction_history.csv",
    "transactions.csv"
]

for filename in files:
    path = data_dir / filename if (data_dir / filename).exists() else Path(filename)
    if path.exists():
        df = pd.read_csv(path, encoding="latin-1")
        print("\n" + "="*50)
        print(f"FILE: {filename}")
        print("Shape:", df.shape)
        print("Columns:", df.columns.tolist()[:10], "... (total", len(df.columns), ")")
        print("Missing values:", df.isnull().sum().sum())
        display(df.head(2))
    else:
        print(f"File not found: {filename}")
```

*Note on Datasets:* `dataco_sample.csv` contains supply chain transaction features with delivery durations and delay indicators. `clients.csv` and `transactions.csv` represent bank account and card transaction records from IBM LinuxONE demo labs.

---

## ⚡ 5. LangGraph & LangSmith Configuration

### Orchestration Graph (`src/workflow.py`)
```
START ──> [ Detection Agent ] ──> [ Risk Agent (ML) ] ──> [ Recommendation Agent ] ──> [ Explanation Agent ] ──> [ Response Assembly ] ──> END
```

### Enabling LangSmith Tracing (`.env`):
```bash
LANGSMITH_TRACING=true
LANGSMITH_API_KEY="your-api-key-here"
LANGSMITH_PROJECT="chainsentinel"
```
When `LANGSMITH_TRACING=true`, every agent invocation, latency, and intermediate state transition is traced automatically in LangSmith.

---

## 🚀 6. Backend API Endpoints (`src/server.py`)

| Endpoint | Method | Description |
| :--- | :---: | :--- |
| **`/health`** | `GET` | Verifies backend, agent readiness, and IBM LinuxONE platform status |
| **`/transactions`** | `GET` | Returns list of recently evaluated transactions |
| **`/alerts`** | `GET` | Returns active high-risk disruption incidents |
| **`/analyze`** | `POST` | **Primary agent entry point:** Executes LangGraph multi-agent workflow |
| **`/simulate-disruption`** | `POST` | Triggers controlled Slide 8 demonstration scenario ($1.9M disruption) |
| **`/api/zos-connect/execute`** | `POST` | Commits approved mitigation actions back to Db2 for z/OS (`RC=0000`) |
| **`/docs`** | `GET` | Interactive Swagger UI documentation |

---

## 🧪 7. Running Tests

Run the unit and integration test suites:
```bash
# In active virtual environment:
python tests/test_prediction.py
python tests/test_api.py
```
Expected output:
```text
ALL PREDICTION TESTS PASSED!
ALL API & LANGGRAPH TESTS PASSED!
```

---

## 🎤 8. Presentation Workflow for Judges

1. **Header Badges:** Show *IBM LinuxONE (s390x) Connected* and *Db2 for z/OS Live Stream: ACTIVE*.
2. **Streaming Ticker:** Demonstrate diverse transactions continuously ingesting every 3 seconds across Germany, Japan, UK, USA.
3. **Simulate Disruption:** Click **`⚡ Simulate Slide 8 ($1.9M Disruption)`**.
   * Multi-agent workflow executes in under 120ms.
   * **Order #4471** flagged with **87% Late Risk**, exposing **$1.9M at risk**.
   * **IBM Granite Box:** Displays plain-English rationale.
4. **Approve via z/OS Connect:** Click **`✓ Approve & Execute via z/OS Connect API`**.
   * Toast confirms: `Transaction Committed to Db2 for z/OS (RC=0000 SUCCESS_COMMIT)`.
