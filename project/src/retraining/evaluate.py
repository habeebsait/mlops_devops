import joblib
import pandas as pd
from sklearn.metrics import classification_report
import sys
import os

def evaluate_model(model_path, test_data_path):
    print(f"Evaluating model {model_path} on {test_data_path}")
    
    model = joblib.load(model_path)
    df = pd.read_parquet(test_data_path)
    
    features = ['url_length', 'num_dots', 'num_digits', 'domain_age', 'has_ip', 'suspicious_keywords']
    features = [f for f in features if f in df.columns]
    
    if 'label' not in df.columns:
        print("No labels in test data.")
        return
        
    X = df[features]
    y = df['label']
    
    y_pred = model.predict(X)
    
    report = classification_report(y, y_pred)
    print(report)
    
    # In a real pipeline, we might fail the build if metrics are below threshold
    
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python evaluate.py <model_path> <test_data_path>")
    else:
        evaluate_model(sys.argv[1], sys.argv[2])
