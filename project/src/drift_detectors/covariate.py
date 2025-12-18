import numpy as np
import pandas as pd
from scipy.stats import ks_2samp, chisquare, wasserstein_distance
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import rbf_kernel
from typing import Dict, List, Union

class CovariateDriftDetector:
    def __init__(self):
        pass

    def calculate_psi(self, expected: np.ndarray, actual: np.ndarray, buckets: int = 10) -> float:
        """
        Calculate Population Stability Index (PSI).
        """
        def scale_range(input, min, max):
            input += -(np.min(input))
            input /= np.max(input) / (max - min)
            input += min
            return input

        breakpoints = np.arange(0, buckets + 1) / (buckets) * 100
        breakpoints = np.percentile(expected, breakpoints)
        
        expected_percents = np.histogram(expected, breakpoints)[0] / len(expected)
        actual_percents = np.histogram(actual, breakpoints)[0] / len(actual)
        
        # Avoid division by zero
        expected_percents = np.where(expected_percents == 0, 0.0001, expected_percents)
        actual_percents = np.where(actual_percents == 0, 0.0001, actual_percents)
        
        psi_value = np.sum((actual_percents - expected_percents) * np.log(actual_percents / expected_percents))
        return psi_value

    def calculate_ks(self, reference: np.ndarray, current: np.ndarray) -> float:
        """
        Kolmogorov-Smirnov test. Returns p-value.
        """
        statistic, p_value = ks_2samp(reference, current)
        return p_value

    def calculate_chi_square(self, reference: pd.Series, current: pd.Series) -> float:
        """
        Chi-Square test for categorical variables. Returns p-value.
        """
        # Align categories
        ref_counts = reference.value_counts(normalize=True)
        curr_counts = current.value_counts(normalize=True)
        
        # Create a dataframe to align indices
        df = pd.DataFrame({'ref': ref_counts, 'curr': curr_counts}).fillna(0)
        
        # Convert back to counts for chi-square (approximate based on current size)
        n_curr = len(current)
        f_obs = (df['curr'] * n_curr).values
        f_exp = (df['ref'] * n_curr).values
        
        # Avoid zero expected frequencies
        f_exp = np.where(f_exp == 0, 1e-5, f_exp)
        
        statistic, p_value = chisquare(f_obs, f_exp=f_exp)
        return p_value

    def calculate_mmd(self, X: np.ndarray, Y: np.ndarray, gamma: float = 1.0) -> float:
        """
        Maximum Mean Discrepancy (MMD) using RBF kernel.
        """
        XX = rbf_kernel(X, X, gamma)
        YY = rbf_kernel(Y, Y, gamma)
        XY = rbf_kernel(X, Y, gamma)
        return XX.mean() + YY.mean() - 2 * XY.mean()

    def detect_embedding_drift(self, ref_embeddings: np.ndarray, curr_embeddings: np.ndarray, method='pca') -> float:
        """
        Detect drift in embeddings using PCA reconstruction error or simple distance.
        Here we use Wasserstein distance on the first principal component as a proxy.
        """
        if method == 'pca':
            pca = PCA(n_components=1)
            pca.fit(ref_embeddings)
            
            ref_proj = pca.transform(ref_embeddings).flatten()
            curr_proj = pca.transform(curr_embeddings).flatten()
            
            return wasserstein_distance(ref_proj, curr_proj)
        return 0.0
