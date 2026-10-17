"""
Sample Data Generator matching DataCo Global Supply Chain Dataset Schema.
Allows testing the entire pipeline immediately without waiting for the full 91MB download.
"""
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_sample_dataco(output_path: str, n_rows: int = 5000):
    np.random.seed(42)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    categories = ['Clothing', 'Sports', 'Electronics', 'Footwear', 'Consumer Goods', 'Computers']
    shipping_modes = ['Standard Class', 'Second Class', 'First Class', 'Same Day']
    customer_countries = ['EE. UU.', 'Puerto Rico', 'Canada', 'Mexico']
    order_countries = ['United States', 'France', 'Germany', 'United Kingdom', 'Mexico', 'Australia', 'Japan', 'India']
    order_regions = ['North America', 'Western Europe', 'Central America', 'Oceania', 'South Asia', 'Eastern Asia']
    
    start_date = datetime(2026, 1, 1)
    
    data = []
    for i in range(n_rows):
        order_id = 10000 + i
        order_item_id = 50000 + i
        customer_id = np.random.randint(100, 2000)
        category = np.random.choice(categories)
        shipping_mode = np.random.choice(shipping_modes, p=[0.60, 0.20, 0.15, 0.05])
        
        # Scheduled days based on shipping mode
        mode_scheduled = {
            'Same Day': 0,
            'First Class': 1,
            'Second Class': 2,
            'Standard Class': 4
        }
        scheduled_days = mode_scheduled[shipping_mode]
        
        # Real shipping days with random delay probability
        delay_prob = 0.55 if shipping_mode in ['Standard Class', 'Second Class'] else 0.40
        is_delayed = np.random.rand() < delay_prob
        
        if is_delayed:
            real_days = scheduled_days + np.random.randint(1, 4)
            late_risk = 1
            delivery_status = 'Late delivery'
        else:
            real_days = max(0, scheduled_days - np.random.randint(0, 2))
            late_risk = 0
            delivery_status = 'Shipping on time' if real_days == scheduled_days else 'Advance shipping'
        
        customer_country = np.random.choice(customer_countries, p=[0.7, 0.2, 0.05, 0.05])
        order_country = np.random.choice(order_countries)
        order_region = np.random.choice(order_regions)
        
        quantity = np.random.randint(1, 6)
        item_price = np.random.choice([25.0, 50.0, 120.0, 299.99, 450.0, 1200.0])
        sales = round(quantity * item_price, 2)
        profit = round(sales * np.random.uniform(0.05, 0.35) - (5.0 if is_delayed else 0.0), 2)
        
        order_dt = start_date + timedelta(minutes=int(np.random.randint(0, 300 * 24 * 60)))
        shipping_dt = order_dt + timedelta(days=int(real_days))
        
        data.append({
            'Order Id': order_id,
            'Order Item Id': order_item_id,
            'Customer Id': customer_id,
            'order date (DateOrders)': order_dt.strftime('%m/%d/%Y %H:%M'),
            'shipping date (DateOrders)': shipping_dt.strftime('%m/%d/%Y %H:%M'),
            'Shipping Mode': shipping_mode,
            'Category Name': category,
            'Customer Country': customer_country,
            'Order Country': order_country,
            'Order Region': order_region,
            'Days for shipment (scheduled)': scheduled_days,
            'Days for shipping (real)': real_days,
            'Late_delivery_risk': late_risk,
            'Delivery Status': delivery_status,
            'Order Item Quantity': quantity,
            'Sales': sales,
            'Order Item Total': sales,
            'Benefit per order': profit,
            'Order Profit Per Order': profit,
            'Product Name': f'{category} Item #{np.random.randint(1, 50)}'
        })
        
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    print(f"Generated {n_rows} rows of sample DataCo dataset at: {output_path}")

if __name__ == '__main__':
    target = os.path.join(os.path.dirname(__file__), '..', 'data', 'dataco_sample.csv')
    generate_sample_dataco(target, n_rows=5000)
