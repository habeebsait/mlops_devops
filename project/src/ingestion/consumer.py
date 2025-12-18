from kafka import KafkaConsumer
import json
from src.ingestion.feature_store import FeatureStore
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PhishingLogConsumer:
    def __init__(self, bootstrap_servers='localhost:9094', topic='phishing_logs', group_id='phishing_monitor'):
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id=group_id,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        self.feature_store = FeatureStore()
        self.batch_size = 100
        self.buffer = []

    def start(self):
        logger.info("Starting consumer...")
        try:
            for message in self.consumer:
                log_entry = message.value
                self.buffer.append(log_entry)
                
                if len(self.buffer) >= self.batch_size:
                    self.flush()
                    
        except KeyboardInterrupt:
            logger.info("Stopping consumer...")
        finally:
            self.flush()
            self.consumer.close()

    def flush(self):
        if self.buffer:
            logger.info(f"Flushing {len(self.buffer)} records to feature store")
            self.feature_store.write_batch(self.buffer)
            self.buffer = []

if __name__ == "__main__":
    # Wait for Kafka to be ready in a real setup
    time.sleep(10) 
    consumer = PhishingLogConsumer()
    consumer.start()
