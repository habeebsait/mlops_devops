from river import drift
from typing import Dict, Any

class ConceptDriftDetector:
    def __init__(self, method: str = 'ADWIN'):
        self.method_name = method
        self._init_detector()
        self.drift_detected = False

    def _init_detector(self):
        if self.method_name == 'ADWIN':
            self.detector = drift.ADWIN()
        elif self.method_name == 'DDM':
            self.detector = drift.binary.DDM()
        elif self.method_name == 'EDDM':
            self.detector = drift.binary.EDDM()
        else:
            raise ValueError(f"Unknown drift detection method: {self.method_name}")

    def update(self, value: float) -> bool:
        """
        Update the detector with a new value (e.g., error rate, 0/1 for correct/incorrect).
        Returns True if drift is detected.
        """
        self.detector.update(value)
        self.drift_detected = self.detector.drift_detected
        return self.drift_detected

    def reset(self):
        self._init_detector()
        self.drift_detected = False
