#!/bin/bash

# Define project root
PROJECT_ROOT="/path/to/project"

# Activate virtualenv
source $PROJECT_ROOT/venv/bin/activate

# Run drift checks
python $PROJECT_ROOT/scripts/batch_psi_check.py
python $PROJECT_ROOT/scripts/batch_ks_check.py
python $PROJECT_ROOT/scripts/batch_prediction_drift.py
python $PROJECT_ROOT/scripts/batch_embedding_drift.py

# Generate Report
python $PROJECT_ROOT/scripts/batch_generate_report.py

# Optional: Check for drift flag and retrain
if grep -q "drift_detected\": true" $PROJECT_ROOT/data/drift_reports/daily_summary_*.json; then
    echo "Drift detected. Triggering retraining..."
    python $PROJECT_ROOT/src/retraining/train.py
fi
