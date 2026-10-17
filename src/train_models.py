"""
Model Training Script for ChainSentinel (Member 3).
Trains:
1. Binary Risk Classifier (XGBoost / RandomForest)
2. Multi-Output Duration Regressor (Fastest & Normal Shipping Days)
Saves artifacts to ../models/ for backend/dashboard consumption.
"""
import os
import joblib
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score, mean_absolute_error, confusion_matrix
from sklearn.multioutput import MultiOutputRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

# Try to import XGBoost, fallback to RandomForest if not yet installed
try:
    from xgboost import XGBClassifier, XGBRegressor
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False

from data_pipeline import load_and_clean_data, prepare_features_and_targets, build_preprocessor

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, '..', 'data')
    models_dir = os.path.join(base_dir, '..', 'models')
    os.makedirs(models_dir, exist_ok=True)
    
    # Priority: full dataset if present, else sample dataset
    full_csv = os.path.join(data_dir, 'DataCoSupplyChainDataset.csv')
    sample_csv = os.path.join(data_dir, 'dataco_sample.csv')
    
    if os.path.exists(full_csv):
        csv_path = full_csv
        print(f"[Data] Using full dataset: {full_csv}")
    elif os.path.exists(sample_csv):
        csv_path = sample_csv
        print(f"[Data] Using sample dataset: {sample_csv}")
    else:
        print("[Data] Generating sample dataset first...")
        from create_sample_data import generate_sample_dataco
        generate_sample_dataco(sample_csv, n_rows=5000)
        csv_path = sample_csv

    print("[Pipeline] Loading and preprocessing data...")
    df = load_and_clean_data(csv_path)
    X_df, y_clf, y_reg, sales, cat_cols, num_cols = prepare_features_and_targets(df)
    
    print(f"[Features] Categorical: {cat_cols}")
    print(f"[Features] Numerical: {num_cols}")
    print(f"[Dataset] Total samples: {len(X_df)}")
    
    # Strict Train/Test split BEFORE preprocessing (prevent leakage)
    X_train_df, X_test_df, y_clf_train, y_clf_test, y_reg_train, y_reg_test, sales_train, sales_test = train_test_split(
        X_df, y_clf, y_reg, sales, test_size=0.2, random_state=42, stratify=y_clf
    )
    
    print("[Preprocessing] Fitting ColumnTransformer on training split only...")
    preprocessor = build_preprocessor(cat_cols, num_cols)
    X_train = preprocessor.fit_transform(X_train_df)
    X_test = preprocessor.transform(X_test_df)
    
    # ---------------------------------------------------------
    # 1. Model 1: Binary Late Delivery Risk Classifier
    # ---------------------------------------------------------
    print("\n--- Training Model 1: Disruption Risk Classifier ---")
    if HAS_XGBOOST:
        print("[Algorithm] Using XGBClassifier (Matches Pitch Deck)")
        clf = XGBClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            eval_metric="logloss",
            random_state=42
        )
    else:
        print("[Algorithm] Using RandomForestClassifier")
        clf = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
        
    clf.fit(X_train, y_clf_train)
    y_clf_pred = clf.predict(X_test)
    y_clf_prob = clf.predict_proba(X_test)[:, 1]
    
    print("Classification Report:")
    print(classification_report(y_clf_test, y_clf_pred, target_names=['On-Time', 'Late Risk']))
    auc = roc_auc_score(y_clf_test, y_clf_prob)
    print(f"ROC-AUC Score: {auc:.4f}")
    
    # ---------------------------------------------------------
    # 2. Model 2: Multi-Output Duration Regressor
    # ---------------------------------------------------------
    print("\n--- Training Model 2: Multi-Output Duration Regressor ---")
    if HAS_XGBOOST:
        base_reg = XGBRegressor(n_estimators=80, max_depth=4, random_state=42)
    else:
        base_reg = RandomForestRegressor(n_estimators=80, max_depth=6, random_state=42)
        
    reg = MultiOutputRegressor(base_reg)
    reg.fit(X_train, y_reg_train)
    y_reg_pred = reg.predict(X_test)
    
    mae_fastest = mean_absolute_error(y_reg_test[:, 0], y_reg_pred[:, 0])
    mae_normal = mean_absolute_error(y_reg_test[:, 1], y_reg_pred[:, 1])
    print(f"Mean Absolute Error (Fastest Duration): {mae_fastest:.2f} days")
    print(f"Mean Absolute Error (Normal Duration):  {mae_normal:.2f} days")
    
    # ---------------------------------------------------------
    # 3. Dollar-at-Risk Calculation (Hackathon Winning Metric)
    # ---------------------------------------------------------
    dollar_at_risk_total = np.sum(y_clf_prob * sales_test)
    print(f"\n[Financial Impact] Total Dollar-at-Risk Identified in Test Set: ${dollar_at_risk_total:,.2f}")
    
    # ---------------------------------------------------------
    # 4. Save Artifacts for Team
    # ---------------------------------------------------------
    print("\n[Export] Saving models to /models directory...")
    joblib.dump(clf, os.path.join(models_dir, 'risk_classifier.joblib'))
    joblib.dump(reg, os.path.join(models_dir, 'duration_regressor.joblib'))
    joblib.dump(preprocessor, os.path.join(models_dir, 'preprocessor.joblib'))
    joblib.dump({'cat_cols': cat_cols, 'num_cols': num_cols}, os.path.join(models_dir, 'metadata.joblib'))
    
    print("SUCCESS: All models and preprocessors saved!")

if __name__ == '__main__':
    main()
