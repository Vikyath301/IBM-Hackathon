"""
Data Preprocessing Pipeline for ChainSentinel.
Handles data loading, cleaning, leakage removal, feature engineering, and train/test splitting.
"""
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer

# Leakage columns that MUST be dropped during training
LEAKAGE_COLUMNS = [
    'Days for shipping (real)',
    'Delivery Status',
    'Order Status',
    'shipping date (DateOrders)'
]

def load_and_clean_data(file_path: str) -> pd.DataFrame:
    """Loads CSV and applies standard initial cleaning."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Data file not found at: {file_path}")
        
    df = pd.read_csv(file_path, encoding='latin-1')
    
    # Clean whitespace in column names
    df.columns = df.columns.str.strip()
    
    # Convert dates to datetime
    if 'order date (DateOrders)' in df.columns:
        df['order_date'] = pd.to_datetime(df['order date (DateOrders)'])
        df['order_hour'] = df['order_date'].dt.hour
        df['order_day_of_week'] = df['order_date'].dt.dayofweek
        df['order_month'] = df['order_date'].dt.month
    else:
        df['order_hour'] = 12
        df['order_day_of_week'] = 2
        df['order_month'] = 6
        
    # Geographic feature: Inland vs International
    if 'Customer Country' in df.columns and 'Order Country' in df.columns:
        df['is_international'] = (df['Customer Country'].astype(str) != df['Order Country'].astype(str)).astype(int)
    else:
        df['is_international'] = 0
        
    # Ensure sales and scheduled days exist
    if 'Sales' not in df.columns and 'Order Item Total' in df.columns:
        df['Sales'] = df['Order Item Total']
        
    return df

def prepare_features_and_targets(df: pd.DataFrame):
    """
    Separates features (X) and targets (y_clf, y_reg) ensuring ZERO data leakage.
    Target 1: Late_delivery_risk (0 or 1)
    Target 2: [Fastest_Days, Normal_Days]
    """
    # Define targets
    y_clf = df['Late_delivery_risk'].values
    
    # Normal days is scheduled days
    normal_days = df['Days for shipment (scheduled)'].values
    # Fastest days estimated as scheduled_days - 1 (min 0)
    fastest_days = np.maximum(0, normal_days - 1)
    y_reg = np.column_stack([fastest_days, normal_days])
    
    # Store sales for financial risk calculation
    sales = df['Sales'].values if 'Sales' in df.columns else np.zeros(len(df))
    
    # Drop targets, leakages, and raw high-cardinality IDs from features
    cols_to_drop = set(LEAKAGE_COLUMNS + [
        'Late_delivery_risk', 'order date (DateOrders)', 'order_date',
        'Product Name', 'Customer Id', 'Order Id', 'Order Item Id',
        'Customer Email', 'Customer Password', 'Customer Fname', 'Customer Lname',
        'Product Description', 'Product Image'
    ])
    
    feature_cols = [c for c in df.columns if c not in cols_to_drop]
    X_df = df[feature_cols].copy()
    
    # Categorical and Numerical identification
    cat_cols = [c for c in ['Shipping Mode', 'Category Name', 'Order Region', 'Customer Country'] if c in X_df.columns]
    num_cols = [c for c in ['Days for shipment (scheduled)', 'Order Item Quantity', 'Sales', 'order_hour', 'order_day_of_week', 'order_month', 'is_international'] if c in X_df.columns]
    
    # Filter X_df to only modeled columns
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
