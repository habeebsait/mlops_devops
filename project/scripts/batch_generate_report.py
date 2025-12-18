import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../project'))

import json
import glob
from datetime import datetime

def generate_daily_report():
    today = datetime.utcnow().date()
    report_path = f'data/drift_reports/daily_summary_{today}.json'
    
    summary = {
        'date': str(today),
        'drift_detected': False,
        'details': {}
    }
    
    # Aggregate all reports for today
    report_files = glob.glob(f'data/drift_reports/*_{today}.json')
    
    for file in report_files:
        if 'daily_summary' in file:
            continue
            
        with open(file, 'r') as f:
            data = json.load(f)
            
        report_type = os.path.basename(file).replace(f'_{today}.json', '')
        summary['details'][report_type] = data
        
        # Check if any drift was detected
        for feature, result in data.items():
            if isinstance(result, dict) and result.get('drift_detected'):
                summary['drift_detected'] = True
    
    with open(report_path, 'w') as f:
        json.dump(summary, f, indent=4)
        
    print(f"Daily report generated: {report_path}")
    if summary['drift_detected']:
        print("WARNING: Drift detected in today's batch checks!")

if __name__ == "__main__":
    generate_daily_report()
