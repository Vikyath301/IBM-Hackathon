"""
Real-Time Inference Engine for ChainSentinel.
Takes an incoming transaction / event, preprocesses it, runs both models,
and computes the Dollar-at-Risk + Alert Priority in milliseconds.
"""
import os
import joblib
import pandas as pd
import numpy as np

class DisruptionPredictor:
    def __init__(self, models_dir: str = None):
        if models_dir is None:
            models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'models')
            
        self.clf = joblib.load(os.path.join(models_dir, 'risk_classifier.joblib'))
        self.reg = joblib.load(os.path.join(models_dir, 'duration_regressor.joblib'))
        self.preprocessor = joblib.load(os.path.join(models_dir, 'preprocessor.joblib'))
        self.metadata = joblib.load(os.path.join(models_dir, 'metadata.joblib'))
        
    def predict_event(self, event: dict) -> dict:
        """
        Input: event dictionary (from live IBM Z stream or REST API).
        Output: Risk assessment, duration range, and dollar impact.
        """
        df = pd.DataFrame([event])
        
        # Ensure engineered features exist
        if 'is_international' not in df.columns:
            customer_country = str(event.get('Customer Country', ''))
            order_country = str(event.get('Order Country', ''))
            df['is_international'] = int(customer_country != order_country) if customer_country and order_country else 0
            
        if 'order_hour' not in df.columns:
            df['order_hour'] = 12
        if 'order_day_of_week' not in df.columns:
            df['order_day_of_week'] = 2
        if 'order_month' not in df.columns:
            df['order_month'] = 6
        if 'Sales' not in df.columns:
            df['Sales'] = event.get('Order Item Total', 0.0)
            
        # Select required columns
        cat_cols = self.metadata['cat_cols']
        num_cols = self.metadata['num_cols']
        
        df_model = df[cat_cols + num_cols].fillna({c: 'Unknown' for c in cat_cols})
        df_model = df_model.fillna({c: 0 for c in num_cols})
        
        # Transform features
        X_vec = self.preprocessor.transform(df_model)
        
        # Predict Late Delivery Probability
        late_prob = float(self.clf.predict_proba(X_vec)[0, 1])
        is_high_risk = bool(late_prob >= 0.50)
        
        # Predict Shipping Durations [Fastest, Normal]
        durations = self.reg.predict(X_vec)[0]
        fastest_days = max(1, int(round(durations[0])))
        normal_days = max(fastest_days, int(round(durations[1])))
        
        # Financial Impact: Dollar at Risk
        sales_val = float(event.get('Sales', event.get('Order Item Total', 100.0)))
        dollar_at_risk = round(late_prob * sales_val, 2)
        
        # Alert Level determination
        if late_prob >= 0.75:
            alert_level = "CRITICAL"
        elif late_prob >= 0.50:
            alert_level = "WARNING"
        else:
            alert_level = "NORMAL"
            
        return {
            "order_id": event.get("Order Id", 99999),
            "product_name": event.get("Product Name", "Unknown SKU"),
            "category_name": event.get("Category Name", "General"),
            "order_country": event.get("Order Country", "Global"),
            "order_region": event.get("Order Region", "International"),
            "shipping_mode": event.get("Shipping Mode", "Standard Class"),
            "scheduled_days": int(event.get("Days for shipment (scheduled)", normal_days)),
            "fastest_predicted_days": fastest_days,
            "normal_predicted_days": normal_days,
            "late_delivery_probability": round(late_prob, 4),
            "is_high_risk": is_high_risk,
            "dollar_at_risk": dollar_at_risk,
            "alert_level": alert_level,
            "order_value": sales_val
        }

if __name__ == '__main__':
    predictor = DisruptionPredictor()
    sample_event = {
        "Order Id": 88410,
        "Customer Country": "EE. UU.",
        "Order Country": "France",
        "Order Region": "Western Europe",
        "Shipping Mode": "Standard Class",
        "Category Name": "Electronics",
        "Product Name": "High Performance Server Blade",
        "Days for shipment (scheduled)": 4,
        "Order Item Quantity": 5,
        "Sales": 2450.00
    }
    result = predictor.predict_event(sample_event)
    print("\n--- Live Disruption Assessment ---")
    for k, v in result.items():
        print(f"{k}: {v}")
