import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../project'))

import pandas as pd
import numpy as np
import json
from src.ingestion.feature_store import FeatureStore
from src.drift_detectors.prediction import PredictionDriftDetector
from src.drift_detectors.rules import DriftRules
from datetime import datetime, timedelta

def run_prediction_drift_check():
    fs = FeatureStore()
    detector = PredictionDriftDetector()
    rules = DriftRules()
    
    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=1)
    baseline_start = today - timedelta(days=30)
    
    current_data = fs.read_window(str(yesterday), str(today))
    baseline_data = fs.read_window(str(baseline_start), str(yesterday))
    
    if current_data.empty or baseline_data.empty:
        print("Insufficient data for Prediction Drift check")
        return

    drift_report = {}
    
    if 'probability' in current_data.columns and 'probability' in baseline_data.columns:
        # Bin probabilities to create distributions
        bins = np.linspace(0, 1, 11)
        curr_hist, _ = np.histogram(current_data['probability'], bins=bins, density=True)
        base_hist, _ = np.histogram(baseline_data['probability'], bins=bins, density=True)
        
        kl = detector.calculate_kl_divergence(base_hist, curr_hist)
        is_drift = rules.check_threshold('prediction', 'kl_divergence', kl)
        
        drift_report['probability'] = {
            'kl_divergence': kl,
            'drift_detected': is_drift
        }
        
        if is_drift:
            print(f"PREDICTION DRIFT DETECTED: KL Divergence = {kl}")
    
    with open(f'data/drift_reports/prediction_report_{today}.json', 'w') as f:
        json.dump(drift_report, f, indent=4)

if __name__ == "__main__":
    os.makedirs('data/drift_reports', exist_ok=True)
    run_prediction_drift_check()
