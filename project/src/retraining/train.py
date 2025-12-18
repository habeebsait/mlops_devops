import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score
import joblib
import os
from datetime import datetime
from src.ingestion.feature_store import FeatureStore

def train_model():
    print("Starting automated retraining...")
    fs = FeatureStore()
    
    # In a real scenario, we would load labelled data from a specific 'labels' store
    # For this demo, we assume we can read from the feature store and there is a 'label' column
    # We'll mock this by loading recent data and assuming a label column exists or creating a dummy one
    
    # Load last 30 days of data
    today = datetime.utcnow().date()
    start_date = today - pd.Timedelta(days=30)
    
    df = fs.read_window(str(start_date), str(today))
    
    if df.empty:
        print("No data found for retraining.")
        return

    # Mock label if not present (for runnable demo)
    if 'label' not in df.columns:
        print("WARNING: 'label' column not found. Creating dummy labels for demonstration.")
        import numpy as np
        df['label'] = np.random.randint(0, 2, size=len(df))

    # Features to use
    features = ['url_length', 'num_dots', 'num_digits', 'domain_age', 'has_ip', 'suspicious_keywords']
    # Ensure features exist
    features = [f for f in features if f in df.columns]
    
    X = df[features]
    y = df['label']
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    
    print(f"Model Trained. Accuracy: {acc:.4f}, Precision: {prec:.4f}, Recall: {rec:.4f}")
    
    # Save model
    version = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    model_path = f'models/phishing_model_{version}.pkl'
    os.makedirs('models', exist_ok=True)
    joblib.dump(model, model_path)
    
    print(f"Model saved to {model_path}")
    
    # Save metrics
    metrics = {'accuracy': acc, 'precision': prec, 'recall': rec, 'version': version}
    with open(f'models/metrics_{version}.json', 'w') as f:
        import json
        json.dump(metrics, f)

if __name__ == "__main__":
    train_model()
