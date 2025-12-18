# Model Monitoring & Drift Detection in Phishing Detection

This project implements a comprehensive production-ready system for monitoring a deployed phishing detection model. It detects Data Drift, Prediction Drift, Concept Drift, and Embedding Drift, and supports automated retraining.

## 📂 Project Structure

```
project/
│── data/                   # Data storage (Feature Store, Logs)
│── models/                 # Trained models and metrics
│── src/
│   ├── ingestion/          # API, Kafka Producer/Consumer, Schema
│   ├── monitoring/         # Monitoring logic
│   ├── drift_detectors/    # Drift detection algorithms (PSI, KS, River, etc.)
│   ├── dashboards/         # Dashboard scripts (Evidently)
│   ├── retraining/         # Automated retraining pipeline
│   ├── utils/              # Utilities (Alert Manager)
│── scripts/                # Batch monitoring scripts
│── dags/                   # Airflow DAGs
│── infra/                  # Infrastructure config (Grafana)
│── docker/                 # Docker configuration
│── tests/                  # Unit tests
│── requirements.txt        # Python dependencies
│── README.md               # This file
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Docker & Docker Compose

### Installation

1.  **Clone the repository**
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

### Running Locally (Docker)

To start Kafka, Zookeeper, and the API:

```bash
cd docker
docker-compose up --build
```

The API will be available at `http://localhost:8000`.

### 📊 Monitoring Modules

#### 1. Data Ingestion
- **API**: Send predictions to `POST /predict`.
- **Kafka**: Logs are pushed to `phishing_logs` topic.
- **Consumer**: Reads from Kafka and writes to Feature Store (Parquet).

#### 2. Drift Detection
- **Covariate Drift**: PSI, KS-test, Chi-square, MMD.
- **Prediction Drift**: KL Divergence, JS Divergence.
- **Concept Drift**: Real-time detection using River (ADWIN, DDM).
- **Embedding Drift**: Wasserstein distance on PCA components.

#### 3. Batch Monitoring
Run daily checks manually or via Cron:

```bash
# Run all checks
./scripts/cron_jobs.sh
```

Individual scripts:
- `scripts/batch_psi_check.py`
- `scripts/batch_ks_check.py`
- `scripts/batch_prediction_drift.py`
- `scripts/batch_generate_report.py`

#### 4. Real-time Monitoring
Start the real-time monitor:

```bash
python scripts/realtime_monitor.py
```

#### 5. Dashboards
- **Evidently**: Generate HTML report:
    ```bash
    python src/dashboards/evidently_dashboard.py
    ```
    Open `data/dashboards/evidently_report_YYYY-MM-DD.html`.
- **Grafana**: Import `infra/grafana/dashboards/dashboard.json` into your Grafana instance.

### 🚨 Alerts
Alerts are sent via Slack (webhook) or logged locally to `data/alerts/incident_log.json`. Configure `SLACK_WEBHOOK_URL` env var.

### 🔄 Automated Retraining
Triggered automatically if drift is detected (via Airflow/Cron) or manually:

```bash
python src/retraining/train.py
```

## 🛠 Deployment

- **Airflow**: Copy `dags/drift_check_dag.py` to your Airflow DAGs folder.
- **Cron**: Schedule `scripts/cron_jobs.sh` in crontab.

## 📝 Architecture

1.  **Model Service** -> **API** -> **Kafka**
2.  **Kafka** -> **Consumer** -> **Feature Store (Parquet)**
3.  **Kafka** -> **Real-time Monitor** -> **Alerts**
4.  **Batch Scripts** -> Read **Feature Store** -> **Drift Detection** -> **Reports**
5.  **Orchestrator** -> Triggers **Retraining** if Drift Detected.
