"""
IBM Z Transaction Stream Simulator (Member 1).
Simulates Db2 for z/OS transactional events streamed via IBM Data Gate / Kafka.
Scores disruptions in real time using the ML models built by Member 3.
"""
import os
import time
import json
import pandas as pd
from predict_risk import DisruptionPredictor

def run_stream_simulation(csv_path: str = None, speed_sec: float = 2.0, max_events: int = 10):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if csv_path is None:
        csv_path = os.path.join(base_dir, '..', 'data', 'dataco_sample.csv')
        
    if not os.path.exists(csv_path):
        from create_sample_data import generate_sample_dataco
        generate_sample_dataco(csv_path, n_rows=1000)

    print("================================================================")
    print("   ChainSentinel: IBM Z Live Stream Ingestion & ML Scoring      ")
    print("   Streaming from Db2 for z/OS via IBM Data Gate to Kafka       ")
    print("================================================================\n")

    df = pd.read_csv(csv_path, encoding='latin-1')
    predictor = DisruptionPredictor()
    
    count = 0
    for idx, row in df.iterrows():
        count += 1
        if count > max_events:
            break
            
        event = row.to_dict()
        order_id = event.get('Order Id', idx)
        
        print(f"[{time.strftime('%H:%M:%S')}] [Db2 for z/OS] New Transaction Event #TXN-{order_id}")
        print(f"  |-> Category: {event.get('Category Name')} | Destination: {event.get('Order Country')} | Mode: {event.get('Shipping Mode')}")
        
        # Scoring in milliseconds
        t0 = time.time()
        assessment = predictor.predict_event(event)
        latency_ms = round((time.time() - t0) * 1000, 2)
        
        prob = assessment['late_delivery_probability']
        alert = assessment['alert_level']
        dollar_risk = assessment['dollar_at_risk']
        fastest = assessment['fastest_predicted_days']
        normal = assessment['normal_predicted_days']
        
        if alert == "CRITICAL":
            badge = "[CRITICAL ALERT]"
        elif alert == "WARNING":
            badge = "[WARNING]"
        else:
            badge = "[NORMAL]"
            
        print(f"  |-> [ML Score {latency_ms}ms] {badge} Late Risk: {prob*100:.1f}% | Dollar-at-Risk: ${dollar_risk:,.2f}")
        print(f"  |-> [Shipping Window] Fastest: {fastest} days | Normal: {normal} days | Scheduled: {assessment['scheduled_days']} days")
        
        if assessment['is_high_risk']:
            print(f"  |==> [ALERT] Triggering Decision Engine & GenAI Explanation...")
            print(f"  |==> [z/OS Connect API] Ready to push rerouting back to IBM Z\n")
        else:
            print(f"  |==> Status Healthy. No corrective intervention required.\n")
            
        time.sleep(speed_sec)

    print("Simulation batch completed successfully.")

if __name__ == '__main__':
    run_stream_simulation(speed_sec=1.5, max_events=5)
