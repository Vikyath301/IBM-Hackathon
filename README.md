# ChainSentinel: Member 1 & Member 3 Pipeline

Welcome to the data and machine learning foundation of **ChainSentinel** for the IBM Z Datathon!

## Directory Layout
```
chainsentinel/
├── data/
│   ├── dataco_sample.csv               # 5,000-row sample dataset (built-in)
│   └── DataCoSupplyChainDataset.csv    # (Optional) Drop the full 91MB Kaggle CSV here
├── models/
│   ├── risk_classifier.joblib          # Trained Disruption Risk Classifier
│   ├── duration_regressor.joblib       # Multi-Output Fastest & Normal Duration Regressor
│   ├── preprocessor.joblib             # OneHotEncoder & Scaler Pipeline
│   └── metadata.joblib                 # Column metadata
├── src/
│   ├── create_sample_data.py           # Generates sample DataCo CSV if needed
│   ├── data_pipeline.py                # Preprocessing, leakage removal, feature engineering
│   ├── train_models.py                 # Trains models and evaluates metrics
│   ├── predict_risk.py                 # Real-time inference function (API for team)
│   └── stream_simulator.py             # Simulates live IBM Z / Db2 event streaming
└── requirements.txt
```

## How to Run:
1. **Train / Re-train Models:**
   ```bash
   python src/train_models.py
   ```
2. **Run Live IBM Z Stream Simulation:**
   ```bash
   python src/stream_simulator.py
   ```
3. **Using Real Kaggle Data:**
   - Download `DataCoSupplyChainDataset.csv` from Kaggle.
   - Place it inside `data/`.
   - Run `python src/train_models.py`. It will automatically detect it and train on all 180,000 rows!
