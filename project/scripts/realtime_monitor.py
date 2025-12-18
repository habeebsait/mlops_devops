import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from kafka import KafkaConsumer
import json
from src.drift_detectors.concept import ConceptDriftDetector
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealTimeMonitor:
    def __init__(self, bootstrap_servers='localhost:9094', topic='phishing_logs'):
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            auto_offset_reset='latest',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        # Initialize detectors for different metrics
        self.accuracy_detector = ConceptDriftDetector(method='ADWIN')
        self.error_rate_detector = ConceptDriftDetector(method='DDM')
        
    def start(self):
        logger.info("Starting real-time monitor...")
        total_count = 0
        error_count = 0

        for message in self.consumer:
            log_entry = message.value
            metadata = log_entry.get('metadata', {})
            prediction = log_entry.get('prediction', {})
            
            if 'delayed_label' in metadata and metadata['delayed_label'] is not None:
                true_label = metadata['delayed_label']
                pred_label = prediction.get('prediction')
                
                is_error = 1 if true_label != pred_label else 0
                
                # Update stats
                total_count += 1
                error_count += is_error
                current_error_rate = error_count / total_count if total_count > 0 else 0
                
                # Send metrics to dashboard
                self.send_to_dashboard('metric', {
                    'error_rate': current_error_rate,
                    'total_count': total_count
                })

                # Update detectors
                if self.accuracy_detector.update(is_error):
                    self.trigger_alert("Concept Drift (ADWIN) detected on Error Rate!")
                    self.accuracy_detector.reset()
                    
                if self.error_rate_detector.update(is_error):
                    self.trigger_alert("Concept Drift (DDM) detected on Error Rate!")
                    self.error_rate_detector.reset()

    def trigger_alert(self, message):
        logger.warning(f"ALERT: {message}")
        self.send_to_dashboard('alert', {'message': message})

    def send_to_dashboard(self, type, data):
        try:
            import requests
            requests.post('http://localhost:8001/api/metrics', json={'type': type, 'data': data}, timeout=0.1)
        except Exception as e:
            # logger.error(f"Failed to send to dashboard: {e}")
            pass

if __name__ == "__main__":
    monitor = RealTimeMonitor()
    monitor.start()
