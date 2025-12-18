from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['admin@example.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'drift_detection_pipeline',
    default_args=default_args,
    description='Daily drift detection and reporting',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(1),
    tags=['mlops', 'drift'],
) as dag:

    # Task 1: Check PSI
    check_psi = BashOperator(
        task_id='check_psi',
        bash_command='python /opt/airflow/project/scripts/batch_psi_check.py',
    )

    # Task 2: Check KS
    check_ks = BashOperator(
        task_id='check_ks',
        bash_command='python /opt/airflow/project/scripts/batch_ks_check.py',
    )

    # Task 3: Check Prediction Drift
    check_pred_drift = BashOperator(
        task_id='check_prediction_drift',
        bash_command='python /opt/airflow/project/scripts/batch_prediction_drift.py',
    )
    
    # Task 4: Check Embedding Drift
    check_emb_drift = BashOperator(
        task_id='check_embedding_drift',
        bash_command='python /opt/airflow/project/scripts/batch_embedding_drift.py',
    )

    # Task 5: Generate Report
    generate_report = BashOperator(
        task_id='generate_report',
        bash_command='python /opt/airflow/project/scripts/batch_generate_report.py',
    )
    
    # Task 6: Trigger Retraining (Conditional)
    # In a real DAG, we would use a BranchPythonOperator to check if drift was detected
    # and then trigger retraining. For simplicity, we just define the task.
    trigger_retraining = BashOperator(
        task_id='trigger_retraining',
        bash_command='python /opt/airflow/project/src/retraining/train.py',
        trigger_rule='all_done' # Run even if drift checks fail/succeed, logic inside script handles it
    )

    [check_psi, check_ks, check_pred_drift, check_emb_drift] >> generate_report >> trigger_retraining
