# 🛡️ ChainSentinel: AI-Powered Supply Chain Resilience on IBM Z
**Team PingXero | IBM Z Datathon**

Real-time predictive supply chain disruption intelligence with GenAI explanations, built on **IBM LinuxONE (s390x)** and **Db2 for z/OS**.

---

## 📁 Repository Layout
```
chainsentinel/
│
├── data/
│   ├── dataco_sample.csv               # 6,000-row supply chain dataset with calibrated delay physics
│   ├── clients.csv                     # 120 enterprise corporate clients (IBM LinuxONE environment)
│   ├── transaction_history.csv         # 2,500 audited fulfillment records with mitigation trails
│   └── transactions.csv                # 1,000 real-time IBM Z Db2 transactional events
│
├── frontend/                           # Separate, modern, responsive Command Center UI
│   ├── index.html                      # Real-time command center dashboard
│   ├── css/
│   │   ├── style.css                   # Obsidian dark mode design system & tokens
│   │   ├── components.css              # KPI cards, agent graph, tables, 3270 terminal
│   │   └── animations.css              # Pulsing beacons, sweeps, typewriter micro-interactions
│   └── js/
│       ├── app.js                      # Core orchestrator, Slide 8 scenario, z/OS API caller
│       ├── agents.js                   # Interactive LangGraph multi-agent flow visualizer
│       ├── charts.js                   # Leaflet dark route map, SHAP attribution bars, duration gauge
│       └── stream.js                   # IBM Z Db2 CDC real-time event generator
│
├── models/
│   ├── risk_classifier.joblib          # Calibrated XGBoost Disruption Risk Classifier (93.1% ROC-AUC)
│   ├── duration_regressor.joblib       # Multi-Output Shipping Duration Regressor (MAE 0.0d / 0.68d)
│   ├── preprocessor.joblib             # ColumnTransformer (OneHotEncoder + StandardScaler)
│   └── metadata.joblib                 # Feature names, importances, and model metrics
│
├── src/                                # Backend services & agent engine
│   ├── data_pipeline.py                # Zero-leakage data cleaning & feature engineering
│   ├── train_models.py                 # High-accuracy model training & evaluation pipeline
│   ├── predict_risk.py                 # Real-time sub-12ms ML inference & SHAP driver engine
│   ├── stream_simulator.py             # Live IBM Z / Db2 event streaming simulator
│   ├── server.py                       # FastAPI entry point exposing /analyze, /alerts, /dashboard
│   ├── schemas.py                      # Pydantic data contracts for agents and APIs
│   ├── workflow.py                     # LangGraph state graph coordinating all 4 agents
│   ├── create_sample_data.py           # Multi-dataset generator for all 4 data files
│   ├── agents/                         # Modular specialized agents
│   │   ├── __init__.py
│   │   ├── detection_agent.py          # Operational anomaly & SLA triage agent
│   │   ├── risk_agent.py               # ML risk, duration & Dollar-at-Risk agent
│   │   ├── recommendation_agent.py     # Pareto action ranking & ROI agent
│   │   └── explanation_agent.py        # IBM Granite natural language synthesis agent
│   └── static/                         # Static asset sync for direct server serving
│
├── tests/
│   ├── test_prediction.py              # Unit tests for ML predictions & bounds
│   └── test_api.py                     # Integration tests for FastAPI & LangGraph workflow
│
├── ChainSentinel_IBM_Z_Demo.ipynb     # Self-contained IBM LinuxONE demo notebook
├── requirements.txt                    # Project dependencies (pandas, xgboost, scikit-learn, etc.)
├── .env                                # Local secrets & LangSmith config
├── .env.example                        # Template for LangSmith & Watsonx secrets
├── .gitignore
├── README.md
└── TEAM_GUIDE.md                       # Comprehensive team role division & architecture guide
```

---

## 🚀 Quickstart & How to Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Train / Re-train Models (High Accuracy)
```bash
python src/train_models.py
```
* **Classifier Accuracy:** 88.83% | **ROC-AUC:** 0.9306 | **Brier Score:** 0.0801
* **Duration Regressor MAE:** 0.00 days (fastest) | 0.68 days (actual)

### 3. Launch Command Center Server & UI
```bash
python src/server.py
```
Open **[http://localhost:8000](http://localhost:8000)** or **[http://localhost:8000/dashboard](http://localhost:8000/dashboard)** in your browser:
* **Interactive Disruption Simulation:** Click **`⚡ Simulate Slide 8 ($1.9M Disruption)`**
* **Live IBM Z Streaming:** Click **`▶ Start Live IBM Z Stream`**
* **Closed-Loop Mainframe Commit:** Click **`✓ Approve & Commit Mitigation via z/OS Connect API`** (emits Db2 `RC=0000 SUCCESS_COMMIT` in simulated 3270 terminal)
* **Cryptographic Compliance Dossier:** Click **`📄 View Audit Dossier`**

### 4. Run Live IBM Z Stream Simulation (Terminal CLI)
```bash
python src/stream_simulator.py
```

### 5. Run Verification Test Suites
```bash
python tests/test_prediction.py
python tests/test_api.py
```

---

## 🧠 Multi-Agent Architecture (The 4-Stage Flywheel)
```
START ──> [ Detection Agent ] ──> [ Risk Agent (ML) ] ──> [ Recommendation Agent ] ──> [ Explanation Agent ] ──> [ z/OS Commit ] ──> END
```
1. **Detection Agent (`src/agents/detection_agent.py`):** Flags operational anomalies (compressed SLAs, cross-border standard ground transit, bulk unit staging bottlenecks).
2. **Risk Agent (`src/agents/risk_agent.py`):** Scores calibrated disruption probabilities (XGBoost), delivery duration ranges, Dollar-at-Risk financial exposure, and SHAP feature drivers.
3. **Recommendation Agent (`src/agents/recommendation_agent.py`):** Ranks mitigation interventions (Regional supplier volume shift, carrier air expedite, safety stock reserve) with explicit ROI multiples (e.g. 35.4x).
4. **Explanation Agent (`src/agents/explanation_agent.py`):** Synthesizes natural-language executive rationales formatted for **IBM Granite** on s390x.
5. **Closed Loop:** Commits approved mitigation actions back to core systems via **z/OS Connect REST APIs** (`RC=0000 SUCCESS_COMMIT`).
