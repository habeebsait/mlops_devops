import yaml
from typing import Dict, Any

class DriftRules:
    def __init__(self, config_path: str = 'drift_rules.yaml'):
        self.config_path = config_path
        self.rules = self._load_rules()

    def _load_rules(self) -> Dict[str, Any]:
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            # Default rules
            return {
                'covariate': {
                    'psi_threshold': 0.2,
                    'ks_p_value_threshold': 0.05
                },
                'prediction': {
                    'kl_divergence_threshold': 0.1
                },
                'concept': {
                    'adwin_delta': 0.002
                }
            }

    def check_threshold(self, metric_type: str, metric_name: str, value: float) -> bool:
        """
        Check if a metric value exceeds the threshold.
        Returns True if threshold is violated (drift detected).
        """
        threshold = self.rules.get(metric_type, {}).get(f"{metric_name}_threshold")
        if threshold is None:
            return False
            
        # Logic depends on metric. 
        # For PSI, KL: higher is worse (drift).
        # For KS p-value: lower is worse (drift).
        
        if metric_name in ['ks_p_value', 'chi_square_p_value']:
            return value < threshold
        else:
            return value > threshold
