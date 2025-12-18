import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../project'))

import pandas as pd
import json
from src.ingestion.feature_store import FeatureStore
from src.drift_detectors.covariate import CovariateDriftDetector
from src.drift_detectors.rules import DriftRules
from datetime import datetime, timedelta

def run_ks_check():
    fs = FeatureStore()
    detector = CovariateDriftDetector()
    rules = DriftRules()
    
    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=1)
    baseline_start = today - timedelta(days=30)
    
    current_data = fs.read_window(str(yesterday), str(today))
    baseline_data = fs.read_window(str(baseline_start), str(yesterday))
    
    if current_data.empty or baseline_data.empty:
        print("Insufficient data for KS check")
        return

    drift_report = {}
    numerical_features = ['url_length', 'num_dots', 'num_digits', 'domain_age']
    
    for feature in numerical_features:
        if feature in current_data.columns and feature in baseline_data.columns:
            p_value = detector.calculate_ks(baseline_data[feature].values, current_data[feature].values)
            is_drift = rules.check_threshold('covariate', 'ks_p_value', p_value)
            
            drift_report[feature] = {
                'ks_p_value': p_value,
                'drift_detected': is_drift
            }
            
            if is_drift:
                print(f"DRIFT DETECTED in {feature}: KS p-value = {p_value}")
    
    with open(f'data/drift_reports/ks_report_{today}.json', 'w') as f:
        json.dump(drift_report, f, indent=4)

if __name__ == "__main__":
    os.makedirs('data/drift_reports', exist_ok=True)
    run_ks_check()
