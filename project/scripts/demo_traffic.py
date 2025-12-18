import requests
import random
import time
import json
from datetime import datetime

API_URL = "http://localhost:8000/predict"

def generate_feature(is_drifted=False):
    # Normal distribution for url_length: mean=50, std=10
    # Drifted distribution: mean=80, std=15
    if is_drifted:
        url_length = int(random.gauss(80, 15))
        domain_age = int(random.gauss(100, 50)) # Newer domains
    else:
        url_length = int(random.gauss(50, 10))
        domain_age = int(random.gauss(1000, 200))

    return {
        "features": {
            "url_length": max(10, url_length),
            "num_dots": random.randint(1, 5),
            "num_digits": random.randint(0, 10),
            "domain_age": max(1, domain_age),
            "has_ip": 1 if is_drifted and random.random() > 0.8 else 0,
            "suspicious_keywords": random.randint(0, 3),
            "html_features": [random.random() for _ in range(5)],
            "email_metadata": {"sender": "test@example.com"},
            "tfidf_vector": [random.random() for _ in range(10)],
            "embedding": [random.random() for _ in range(5)]
        },
        "prediction": {
            # Simulate model degradation: 
            # If drifted, model might fail to detect it (predict 0 instead of 1)
            "probability": random.uniform(0.1, 0.6) if is_drifted else random.uniform(0.1, 0.4),
            "prediction": 0 if is_drifted and random.random() > 0.2 else (1 if is_drifted else 0),
            "model_version": "v1.0"
        },
        "metadata": {
            "user_agent": "Mozilla/5.0",
            "region": "US",
            "referral": "google",
            "time_of_day": "morning",
            "domain": "example.com",
            "url": "http://example.com/login",
            "hashed_text": "abc123hash",
            "timestamp": datetime.utcnow().isoformat(),
            "delayed_label": 1 if is_drifted else 0 # Simulate perfect labeling for now
        }
    }

def run_simulation():
    print("Starting simulation...")
    
    # 1. Normal Traffic
    print("Sending 50 normal requests...")
    for i in range(50):
        data = generate_feature(is_drifted=False)
        try:
            requests.post(API_URL, json=data)
            print(f".", end="", flush=True)
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(0.1)
    print("\nNormal traffic sent.")

    # 2. Drifted Traffic
    print("\nSending 50 DRIFTED requests...")
    for i in range(50):
        data = generate_feature(is_drifted=True)
        try:
            requests.post(API_URL, json=data)
            print(f"!", end="", flush=True)
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(0.1)
    print("\nDrifted traffic sent.")

if __name__ == "__main__":
    run_simulation()
