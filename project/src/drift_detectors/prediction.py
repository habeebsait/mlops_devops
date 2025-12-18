import numpy as np
from scipy.stats import entropy
from scipy.spatial.distance import jensenshannon
from typing import List

class PredictionDriftDetector:
    def __init__(self):
        pass

    def calculate_kl_divergence(self, p: np.ndarray, q: np.ndarray) -> float:
        """
        Kullback-Leibler divergence.
        p: reference distribution
        q: current distribution
        """
        # Normalize to ensure they sum to 1
        p = p / np.sum(p)
        q = q / np.sum(q)
        
        # Avoid zero probabilities
        p = np.where(p == 0, 1e-10, p)
        q = np.where(q == 0, 1e-10, q)
        
        return entropy(p, q)

    def calculate_js_divergence(self, p: np.ndarray, q: np.ndarray) -> float:
        """
        Jensen-Shannon divergence.
        """
        return jensenshannon(p, q)

    def calculate_entropy_shift(self, p: np.ndarray, q: np.ndarray) -> float:
        """
        Difference in entropy between two distributions.
        """
        return abs(entropy(p) - entropy(q))
