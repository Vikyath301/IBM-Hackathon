"""
Data Preprocessing Pipeline for ChainSentinel.
Handles data loading, cleaning, zero-leakage feature engineering, and ColumnTransformer construction.
"""
import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer

# Leakage columns that MUST NEVER be fed as model input features
LEAKAGE_COLUMNS = [
    'Days for shipping (real)',
    'Delivery Status',
    'Order Status',
    'shipping date (DateOrders)'
]

# Baseline expected days for standard carrier modes
BASELINE_MODE_DAYS = {
    'Same Day': 0,
    'First Class': 1,
    'Second Class': 2,
    'Standard Class': 4,
    'Standard Ground': 4
}

def load_and_clean_data(file_path: str) -> pd.DataFrame:
    """Loads CSV and applies standard initial cleaning and feature engineering."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Data file not found at: {file_path}")
        
    df = pd.read_csv(file_path, encoding='latin-1')
    
    # Clean whitespace in column names
    df.columns = df.columns.str.strip()
    
    # Convert dates to datetime
    if 'order date (DateOrders)' in df.columns:
        df['order_date'] = pd.to_datetime(df['order date (DateOrders)'], errors='coerce')
        df['order_hour'] = df['order_date'].dt.hour.fillna(12).astype(int)
        df['order_day_of_week'] = df['order_date'].dt.dayofweek.fillna(2).astype(int)
        df['order_month'] = df['order_date'].dt.month.fillna(6).astype(int)
    else:
        df['order_hour'] = 12
        df['order_day_of_week'] = 2
        df['order_month'] = 6
        
    # Geographic feature: Inland vs International
    if 'Customer Country' in df.columns and 'Order Country' in df.columns:
        df['is_international'] = (df['Customer Country'].astype(str) != df['Order Country'].astype(str)).astype(int)
    else:
        df['is_international'] = 0

    # Ensure sales exists
    if 'Sales' not in df.columns and 'Order Item Total' in df.columns:
        df['Sales'] = df['Order Item Total']
    elif 'Sales' not in df.columns:
        df['Sales'] = 100.0

    if 'Order Item Quantity' not in df.columns:
        df['Order Item Quantity'] = 1

    # Engineered domain features (Zero Leakage)
    df['is_weekend'] = (df['order_day_of_week'] >= 5).astype(int)
    df['is_high_value'] = (df['Sales'] >= 2000.0).astype(int)
    df['is_bulk_qty'] = (df['Order Item Quantity'] >= 4).astype(int)
    df['unit_price'] = (df['Sales'] / (df['Order Item Quantity'] + 1e-5)).round(2)

    return df

def prepare_features_and_targets(df: pd.DataFrame):
    """
    Separates features (X) and targets (y_clf, y_reg) ensuring ZERO data leakage.
    Target 1: Late_delivery_risk (0 or 1)
    Target 2: [Fastest_Days, Normal_Days] (predicting actual physical delivery range)
    """
    y_clf = df['Late_delivery_risk'].values.astype(int)
    
    # Regression targets:
    # Column 0: Fastest feasible expedited days (air courier minimum)
    # Column 1: Predicted actual duration in days
    if 'Days for shipping (real)' in df.columns:
        actual_real_days = df['Days for shipping (real)'].values.astype(float)
    else:
        actual_real_days = df['Days for shipment (scheduled)'].values.astype(float)

    # Fastest duration is achievable via expedited carrier
    scheduled = df['Days for shipment (scheduled)'].values.astype(float)
    fastest_days = np.maximum(1.0, np.minimum(scheduled, 2.0))
    y_reg = np.column_stack([fastest_days, actual_real_days])
    
    sales = df['Sales'].values.astype(float)
    
    # Drop targets, leakages, and raw high-cardinality IDs from features
    cols_to_drop = set(LEAKAGE_COLUMNS + [
        'Late_delivery_risk', 'order date (DateOrders)', 'order_date',
        'Product Name', 'Customer Id', 'Order Id', 'Order Item Id',
        'Customer Email', 'Customer Password', 'Customer Fname', 'Customer Lname',
        'Product Description', 'Product Image'
    ])
    
    feature_cols = [c for c in df.columns if c not in cols_to_drop]
    X_df = df[feature_cols].copy()
    
    cat_cols = [c for c in ['Shipping Mode', 'Category Name', 'Order Region', 'Customer Country', 'Order Country'] if c in X_df.columns]
    num_cols = [c for c in ['Days for shipment (scheduled)', 'Order Item Quantity', 'Sales', 
                            'order_hour', 'order_day_of_week', 'order_month', 
                            'is_international', 'is_weekend', 'is_high_value', 'is_bulk_qty', 'unit_price'] if c in X_df.columns]
    
    X_df = X_df[cat_cols + num_cols].fillna({c: 'Unknown' for c in cat_cols})
    X_df = X_df.fillna({c: 0 for c in num_cols})
    
    return X_df, y_clf, y_reg, sales, cat_cols, num_cols

def build_preprocessor(cat_cols, num_cols):
    """Creates a ColumnTransformer to encode categoricals and scale numerics."""
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), cat_cols),
            ('num', StandardScaler(), num_cols)
        ]
    )
    return preprocessor
