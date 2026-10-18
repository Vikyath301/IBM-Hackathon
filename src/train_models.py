"""
Model Training Script for ChainSentinel (Member 3).
Trains:
1. Binary Risk Classifier (Calibrated XGBClassifier / RandomForest) with high accuracy
2. Multi-Output Duration Regressor (Fastest & Actual Shipping Days)
Saves artifacts to ../models/ for backend/dashboard consumption.
"""
import os
import joblib
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report,
    roc_auc_score,
    accuracy_score,
    mean_absolute_error,
    confusion_matrix,
    brier_score_loss
)
from sklearn.multioutput import MultiOutputRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingRegressor
from sklearn.calibration import CalibratedClassifierCV

# Try to import XGBoost, fallback to RandomForest if needed
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
        from create_sample_data import generate_all_datasets
        generate_all_datasets(data_dir, n_rows=6000)
        csv_path = sample_csv

    print("[Pipeline] Loading and preprocessing data with zero leakage...")
    df = load_and_clean_data(csv_path)
    X_df, y_clf, y_reg, sales, cat_cols, num_cols = prepare_features_and_targets(df)
    
    print(f"[Features] Categorical ({len(cat_cols)}): {cat_cols}")
    print(f"[Features] Numerical ({len(num_cols)}): {num_cols}")
    print(f"[Dataset] Total samples: {len(X_df)} | Delay Base Rate: {np.mean(y_clf)*100:.1f}%")
    
    # Train/Test split BEFORE preprocessing (prevent leakage)
    X_train_df, X_test_df, y_clf_train, y_clf_test, y_reg_train, y_reg_test, sales_train, sales_test = train_test_split(
        X_df, y_clf, y_reg, sales, test_size=0.2, random_state=42, stratify=y_clf
    )
    
    print("[Preprocessing] Fitting ColumnTransformer on training split...")
    preprocessor = build_preprocessor(cat_cols, num_cols)
    X_train = preprocessor.fit_transform(X_train_df)
    X_test = preprocessor.transform(X_test_df)
    
    # Get feature names after one-hot encoding
    cat_feature_names = preprocessor.named_transformers_['cat'].get_feature_names_out(cat_cols).tolist()
    all_feature_names = cat_feature_names + num_cols
    print(f"[Transformer] Total encoded input dimension: {len(all_feature_names)}")

    # ---------------------------------------------------------
    # 1. Model 1: High-Accuracy Binary Late Delivery Risk Classifier
    # ---------------------------------------------------------
    print("\n=======================================================")
    print("  TRAINING MODEL 1: Disruption Risk Classifier")
    print("=======================================================")
    if HAS_XGBOOST:
        print("[Algorithm] Training optimized XGBClassifier (IBM Z Pitch Spec)...")
        base_clf = XGBClassifier(
            n_estimators=160,
            max_depth=5,
            learning_rate=0.08,
            subsample=0.85,
            colsample_bytree=0.85,
            eval_metric="logloss",
            random_state=42,
            n_jobs=-1
        )
    else:
        print("[Algorithm] Training tuned RandomForestClassifier...")
        base_clf = RandomForestClassifier(
            n_estimators=150,
            max_depth=10,
            min_samples_split=4,
            random_state=42,
            n_jobs=-1
        )
        
    # Calibrate probabilities for reliable Dollar-at-Risk calculation
    print("[Calibration] Calibrating probabilities with CalibratedClassifierCV...")
    clf = CalibratedClassifierCV(estimator=base_clf, method='sigmoid', cv=3)
    clf.fit(X_train, y_clf_train)
    
    y_clf_pred = clf.predict(X_test)
    y_clf_prob = clf.predict_proba(X_test)[:, 1]
    
    acc = accuracy_score(y_clf_test, y_clf_pred)
    auc = roc_auc_score(y_clf_test, y_clf_prob)
    brier = brier_score_loss(y_clf_test, y_clf_prob)
    cm = confusion_matrix(y_clf_test, y_clf_pred)
    
    print(f"\n[Classification Metrics]")
    print(f"Accuracy:         {acc * 100:.2f}%")
    print(f"ROC-AUC Score:    {auc:.4f}")
    print(f"Brier Loss Score: {brier:.4f} (lower is better, <0.10 indicates high calibration)")
    print("\nConfusion Matrix:")
    print(f"  TN: {cm[0,0]:<5} | FP: {cm[0,1]:<5}")
    print(f"  FN: {cm[1,0]:<5} | TP: {cm[1,1]:<5}")
    print("\nDetailed Classification Report:")
    print(classification_report(y_clf_test, y_clf_pred, target_names=['On-Time', 'Late Risk'], digits=4))

    # Extract feature importance weights from base estimator
    # Train one standalone base_clf to extract raw feature importances
    base_clf.fit(X_train, y_clf_train)
    raw_importances = base_clf.feature_importances_
    top_indices = np.argsort(raw_importances)[::-1][:10]
    print("\n[Top 10 Feature Importances]")
    for idx in top_indices:
        print(f"  - {all_feature_names[idx]:<35}: {raw_importances[idx]*100:.2f}%")

    # ---------------------------------------------------------
    # 2. Model 2: Multi-Output Duration Regressor
    # ---------------------------------------------------------
    print("\n=======================================================")
    print("  TRAINING MODEL 2: Multi-Output Duration Regressor")
    print("=======================================================")
    if HAS_XGBOOST:
        base_reg = XGBRegressor(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.08,
            random_state=42,
            n_jobs=-1
        )
    else:
        base_reg = RandomForestRegressor(
            n_estimators=100,
            max_depth=8,
            random_state=42,
            n_jobs=-1
        )
        
    reg = MultiOutputRegressor(base_reg)
    reg.fit(X_train, y_reg_train)
    y_reg_pred = reg.predict(X_test)
    
    mae_fastest = mean_absolute_error(y_reg_test[:, 0], y_reg_pred[:, 0])
    mae_normal = mean_absolute_error(y_reg_test[:, 1], y_reg_pred[:, 1])
    print(f"Mean Absolute Error (Fastest Duration): {mae_fastest:.2f} days")
    print(f"Mean Absolute Error (Actual Duration):  {mae_normal:.2f} days")
    
    # ---------------------------------------------------------
    # 3. Financial Dollar-at-Risk Validation
    # ---------------------------------------------------------
    dollar_at_risk_total = float(np.sum(y_clf_prob * sales_test))
    print(f"\n[Financial Impact] Total Dollar-at-Risk in Test Split: ${dollar_at_risk_total:,.2f}")
    
    # ---------------------------------------------------------
    # 4. Save Artifacts & Rich Metadata
    # ---------------------------------------------------------
    print("\n[Export] Serializing models and metadata to models/ ...")
    joblib.dump(clf, os.path.join(models_dir, 'risk_classifier.joblib'))
    joblib.dump(reg, os.path.join(models_dir, 'duration_regressor.joblib'))
    joblib.dump(preprocessor, os.path.join(models_dir, 'preprocessor.joblib'))
    
    metadata = {
        'cat_cols': cat_cols,
        'num_cols': num_cols,
        'all_feature_names': all_feature_names,
        'feature_importances': dict(zip(all_feature_names, [float(x) for x in raw_importances])),
        'test_accuracy': float(acc),
        'test_auc': float(auc),
        'mae_fastest': float(mae_fastest),
        'mae_normal': float(mae_normal)
    }
    joblib.dump(metadata, os.path.join(models_dir, 'metadata.joblib'))
    
    print("SUCCESS: High-accuracy models and feature metadata successfully saved!")

if __name__ == '__main__':
    main()
