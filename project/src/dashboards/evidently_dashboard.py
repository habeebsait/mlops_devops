import pandas as pd
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, TargetDriftPreset, DataQualityPreset
from evidently.test_suite import TestSuite
from evidently.test_preset import DataDriftTestPreset
from src.ingestion.feature_store import FeatureStore
from datetime import datetime, timedelta
import os

def generate_evidently_report():
    fs = FeatureStore()
    
    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=1)
    baseline_start = today - timedelta(days=30)
    
    current_data = fs.read_window(str(yesterday), str(today))
    baseline_data = fs.read_window(str(baseline_start), str(yesterday))
    
    if current_data.empty or baseline_data.empty:
        print("Insufficient data for Evidently report")
        return

    # Generate Data Drift Report
    report = Report(metrics=[
        DataDriftPreset(),
        TargetDriftPreset(),
        DataQualityPreset()
    ])
    
    report.run(reference_data=baseline_data, current_data=current_data)
    
    output_path = f'data/dashboards/evidently_report_{today}.html'
    os.makedirs('data/dashboards', exist_ok=True)
    report.save_html(output_path)
    print(f"Evidently report saved to {output_path}")

    # Run Test Suite (for automated checks)
    tests = TestSuite(tests=[
        DataDriftTestPreset()
    ])
    tests.run(reference_data=baseline_data, current_data=current_data)
    tests.save_html(f'data/dashboards/evidently_tests_{today}.html')

if __name__ == "__main__":
    generate_evidently_report()
