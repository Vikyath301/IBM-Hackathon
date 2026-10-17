# 🛡️ ChainSentinel: Master Team & Handover Guide
**Team PingXero | IBM Z Datathon**

This document contains everything built, configured, and tested for the **ChainSentinel** project. Any team member or AI assistant can read this guide to immediately understand the project, run the code, and continue development.

---

## 📌 1. Project Overview & Pitch
* **Tagline:** Real-time predictive supply chain disruption intelligence with GenAI explanations, built on IBM Z.
* **Problem:** Critical supply chain events (delayed shipments, stockouts, demand surges) happen in seconds, but operational teams detect them days later due to siloed batch reporting and black-box alert fatigue.
* **Solution (The 4-Stage Flywheel):**
  1. **Detect:** Real-time stream anomaly detection on orders, shipments, and inventory from Db2 for z/OS.
  2. **Predict:** Machine learning (XGBoost/RandomForest) calculates disruption probabilities and financial dollar-at-risk per SKU.
  3. **Recommend:** A prescriptive decision engine evaluates supplier alternatives, route feasibility, and expedite costs.
  4. **Explain:** IBM Granite Generative AI layer translates complex model outputs into human-readable executive summaries.
  5. **Closed Loop:** Corrective actions are committed back to Db2 for z/OS via **z/OS Connect REST APIs** (`RC=0000`).

---

## 👥 2. 6-Member Team Role Division

| Member | Role | Deliverables & Status |
| :--- | :--- | :--- |
| **Member 1** | Data Engineer & Mainframe Simulator | `src/stream_simulator.py`, `data/dataco_sample.csv` (Simulates Db2 log stream) — ✅ Complete |
| **Member 2** | Backend & z/OS Connect API | `src/server.py`, `src/test_api.py` (FastAPI REST server & z/OS Gateway) — ✅ Complete |
| **Member 3** | ML & Predictive Analytics Lead | `src/data_pipeline.py`, `src/train_models.py`, `models/` (Risk & Duration AI) — ✅ Complete |
| **Member 4** | Prescriptive Decision & GenAI | Decision ranking + IBM Granite plain-language alert explanations — ✅ Complete |
| **Member 5** | Frontend & Live Command Center | `src/static/index.html` (Dark-mode responsive command center UI) — ✅ Complete |
| **Member 6** | Pitch Deck & Demo Video | 10-slide deck (Team PingXero PPT), presentation script, video demo — ⏳ In Progress |

---

## 🔗 3. Key Links & File Locations

* **GitHub Repository:** [https://github.com/pavanpoojary348/chainsentinel](https://github.com/pavanpoojary348/chainsentinel)
* **IBM LinuxONE Server:** `http://148.100.109.180:38888/tree?`
* **Local Web Dashboard:** `http://localhost:8000` (or `http://localhost:8000/dashboard`)
* **Local API Swagger Docs:** `http://localhost:8000/docs`
* **Public Web Link (Localtunnel):** `https://brave-cloths-stay.loca.lt` *(Password: `103.167.211.189`)*

---

## ☁️ 4. How to Run on IBM LinuxONE (JupyterLab)

1. Open `http://148.100.109.180:38888/tree?` in your browser.
2. Ensure both **`ChainSentinel_IBM_Z_Demo.ipynb`** and **`dataco_sample.csv`** are uploaded in your file list.
3. Open `ChainSentinel_IBM_Z_Demo.ipynb`.
4. Click **Kernel $\rightarrow$ Restart & Run All Cells**.
5. **CRITICAL:** Take a screenshot of **Step 1** showing:
   ```text
   System Architecture: s390x (IBM LinuxONE / z/OS)
   ```
   Add this screenshot to **Slide 6 & 7** of the pitch deck to prove the AI runs natively on IBM Z hardware!

---

## 💻 5. How to Run the Server & Dashboard on Your Laptop

```bash
# 1. Clone the repository
git clone https://github.com/pavanpoojary348/chainsentinel.git
cd chainsentinel

# 2. Create virtual environment & install requirements
python -m venv .venv

# On Windows:
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\python src/server.py

# On Linux/Mac:
source .venv/bin/activate
pip install -r requirements.txt
python src/server.py
```
Open **`http://localhost:8000`** in Chrome/Edge to interact with the live command center.

---

## 🎯 6. Slide 8 Interactive Demo Workflow (What to Show Judges)

1. **Top Header:** Point out the pulsing green badges: *IBM LinuxONE (s390x) Connected* and *Db2 for z/OS Live Stream: ACTIVE*.
2. **Live Ingestion Feed:** Show orders continuously rolling in every 3 seconds from Germany, Japan, UK, USA with diverse risk ratings.
3. **Trigger Disruption:** Click **`⚡ Simulate Slide 8 ($1.9M Disruption)`**.
   * Live timer banner appears: *Under 5-second decision latency*.
   * **Order #4471** pops up with **87% Late Risk**, putting **$1.9M at risk**.
   * **IBM Granite GenAI Box:** Displays the plain-English executive explanation:
     > *"High risk: Supplier A is 36 hours late, stock covers 4 days, demand is up 18%. Recommended: Shift 60% of volume to Supplier B and reroute shipment 4471. Protects about $1.7M of orders for about $48K added cost."*
4. **Close the Loop:** Click **`✓ Approve & Execute via z/OS Connect API`**.
   * Toast notification confirms: `Transaction Committed to Db2 for z/OS (RC=0000 SUCCESS_COMMIT)`.

---

## 🎤 7. 3-Minute Presentation Script (For Team PingXero)

* **0:00 - 0:30 (Problem):** Supply chain disruptions cost millions because leaders find out days late in static reports. Alerts are reactive, fragmented, and black-box numbers that managers second-guess.
* **0:30 - 1:00 (Solution):** ChainSentinel turns live transactions into trusted decisions in under 5 seconds through a 4-stage flywheel: Detect, Predict, Recommend, Explain.
* **1:00 - 1:45 (Why IBM Z):** Enterprise transactions already live on Db2 for z/OS. Using IBM Data Gate, change logs stream into our AI pipeline without offloading data. Machine learning scores disruption risk, IBM Granite provides plain-English reasons, and z/OS Connect commits actions back to the core.
* **1:45 - 2:30 (Live Demo):** Trigger the Slide 8 simulation, show the 87% late risk alert, read the GenAI explanation, and click Approve via z/OS Connect.
* **2:30 - 3:00 (ROI & Close):** Cuts decision lag from days to seconds, reduces disruption costs by 15-25%, and ensures operations keep running smoothly.
