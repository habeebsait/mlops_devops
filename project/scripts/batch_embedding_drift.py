import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../project'))

import pandas as pd
import numpy as np
import json
from src.ingestion.feature_store import FeatureStore
from src.drift_detectors.covariate import CovariateDriftDetector
from datetime import datetime, timedelta

def run_embedding_drift_check():
    fs = FeatureStore()
    detector = CovariateDriftDetector()
    
    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=1)
    baseline_start = today - timedelta(days=30)
    
    current_data = fs.read_window(str(yesterday), str(today))
    baseline_data = fs.read_window(str(baseline_start), str(yesterday))
    
    if current_data.empty or baseline_data.empty:
        print("Insufficient data for Embedding Drift check")
        return

    drift_report = {}
    
    # Assuming 'embedding' column contains lists/arrays
    if 'embedding' in current_data.columns and 'embedding' in baseline_data.columns:
        # Convert list of lists to numpy array
        curr_emb = np.stack(current_data['embedding'].values)
        base_emb = np.stack(baseline_data['embedding'].values)
        
        # Check drift
        drift_score = detector.detect_embedding_drift(base_emb, curr_emb)
        
        # Simple threshold for demo
        is_drift = drift_score > 0.1
        
        drift_report['embedding'] = {
            'wasserstein_distance': drift_score,
            'drift_detected': is_drift
        }
        
        if is_drift:
            print(f"EMBEDDING DRIFT DETECTED: Score = {drift_score}")
    
    with open(f'data/drift_reports/embedding_report_{today}.json', 'w') as f:
        json.dump(drift_report, f, indent=4)

if __name__ == "__main__":
    os.makedirs('data/drift_reports', exist_ok=True)
    run_embedding_drift_check()
