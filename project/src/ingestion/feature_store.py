import pandas as pd
import os
from datetime import datetime
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeatureStore:
    def __init__(self, base_path='data/feature_store'):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)

    def write_batch(self, logs: List[Dict]):
        """
        Writes a batch of logs to Parquet, partitioned by date.
        """
        if not logs:
            return

        df = pd.DataFrame(logs)
        
        # Flatten nested structures if necessary or keep as JSON strings for complex types
        # For simplicity, we assume flat structure or handle it downstream
        # But here we might want to normalize. 
        # Let's normalize the 'features', 'prediction', 'metadata' columns
        
        # A better approach for Parquet is to have flat columns
        flat_logs = []
        for log in logs:
            flat_log = {}
            flat_log.update(log.get('features', {}))
            flat_log.update(log.get('prediction', {}))
            flat_log.update(log.get('metadata', {}))
            flat_logs.append(flat_log)
            
        df = pd.DataFrame(flat_logs)
        
        # Partition by date
        today = datetime.utcnow().strftime('%Y-%m-%d')
        partition_path = os.path.join(self.base_path, f"date={today}")
        os.makedirs(partition_path, exist_ok=True)
        
        filename = f"batch_{datetime.utcnow().timestamp()}.parquet"
        file_path = os.path.join(partition_path, filename)
        
        df.to_parquet(file_path, index=False)
        logger.info(f"Written {len(logs)} records to {file_path}")

    def read_window(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Reads data within a date range.
        Dates should be in 'YYYY-MM-DD' format.
        """
        # This is a simplified reader. In production, use a query engine or smarter partition pruning.
        # We will iterate over directories.
        
        all_dfs = []
        # Simple directory walk - in real app, parse dates from folder names
        for root, dirs, files in os.walk(self.base_path):
            for file in files:
                if file.endswith(".parquet"):
                    # Extract date from path
                    # path is data/feature_store/date=YYYY-MM-DD/file.parquet
                    # We can check if the folder date is within range
                    # This is a basic implementation
                    full_path = os.path.join(root, file)
                    try:
                        df = pd.read_parquet(full_path)
                        # Filter by timestamp if needed, but partition is usually enough for coarse grain
                        all_dfs.append(df)
                    except Exception as e:
                        logger.error(f"Error reading {full_path}: {e}")
                        
        if not all_dfs:
            return pd.DataFrame()
            
        return pd.concat(all_dfs, ignore_index=True)
