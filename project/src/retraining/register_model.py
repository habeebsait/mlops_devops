import sys
import os
import shutil

def register_model(model_path):
    """
    Simulates registering a model to a production registry (e.g., MLflow, S3).
    Here we just copy it to a 'production' folder.
    """
    if not os.path.exists(model_path):
        print(f"Model {model_path} does not exist.")
        return

    prod_dir = 'models/production'
    os.makedirs(prod_dir, exist_ok=True)
    
    filename = os.path.basename(model_path)
    prod_path = os.path.join(prod_dir, 'current_model.pkl')
    
    # Backup existing
    if os.path.exists(prod_path):
        backup_path = os.path.join(prod_dir, f"backup_{filename}")
        shutil.copy(prod_path, backup_path)
        
    shutil.copy(model_path, prod_path)
    print(f"Model registered to {prod_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python register_model.py <model_path>")
    else:
        register_model(sys.argv[1])
