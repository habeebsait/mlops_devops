import json
from kafka import KafkaProducer
from src.ingestion.schema import LogEntry
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PhishingLogProducer:
    def __init__(self, bootstrap_servers='localhost:9094', topic='phishing_logs'):
        self.topic = topic
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v.dict(), default=str).encode('utf-8')
        )

    def send_log(self, log_entry: LogEntry):
        try:
            self.producer.send(self.topic, log_entry)
            self.producer.flush()
            logger.info(f"Sent log to topic {self.topic}")
        except Exception as e:
            logger.error(f"Failed to send log: {e}")

    def close(self):
        self.producer.close()
