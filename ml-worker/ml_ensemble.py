import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.neural_network import MLPRegressor
from sklearn.cluster import KMeans


class FeatureNormalizer:
    def __init__(self):
        self.means_ = None
        self.stds_ = None
        self.feature_names_ = None

    def fit(self, X):
        if isinstance(X, pd.DataFrame):
            self.feature_names_ = X.columns.tolist()
            X = X.values
        else:
            self.feature_names_ = [f"feature_{i}" for i in range(X.shape[1])]
        self.means_ = np.mean(X, axis=0)
        self.stds_ = np.std(X, axis=0)
        self.stds_[self.stds_ == 0] = 1.0
        return self

    def transform(self, X):
        if isinstance(X, pd.DataFrame):
            X = X.values
        return (X - self.means_) / self.stds_

    def fit_transform(self, X):
        return self.fit(X).transform(X)


class AutoencoderAnomalyDetector:
    def __init__(self, random_state=42):
        self.model = None
        self.is_trained = False
        self.random_state = random_state

    def fit(self, X):
        n_features = X.shape[1]
        hidden_size = max(n_features * 2, 16)
        bottleneck_size = max(n_features // 2, 4)
        self.model = MLPRegressor(
            hidden_layer_sizes=(hidden_size, bottleneck_size, hidden_size),
            activation='relu',
            solver='adam',
            max_iter=1000,
            random_state=self.random_state,
            early_stopping=True,
            validation_fraction=0.1,
            n_iter_no_change=10,
        )
        self.model.fit(X, X)
        self.is_trained = True

    def predict(self, X):
        if not self.is_trained:
            raise ValueError("Model not trained yet")
        reconstruction = self.model.predict(X)
        mse = np.mean((X - reconstruction) ** 2, axis=1)
        if mse.max() == mse.min():
            return np.zeros_like(mse)
        scores = (mse - mse.min()) / (mse.max() - mse.min() + 1e-9)
        return scores


class ClusteringAnomalyDetector:
    def __init__(self, random_state=42):
        self.model = None
        self.is_trained = False
        self.random_state = random_state
        self.n_clusters = None

    def fit(self, X):
        n_samples = X.shape[0]
        self.n_clusters = max(2, n_samples // 10)
        self.model = KMeans(n_clusters=self.n_clusters, random_state=self.random_state, n_init='auto')
        self.model.fit(X)
        self.is_trained = True

    def predict(self, X):
        if not self.is_trained:
            raise ValueError("Model not trained yet")
        distances = []
        centers = self.model.cluster_centers_
        for x in X:
            dists = np.linalg.norm(centers - x.reshape(1, -1), axis=1)
            distances.append(np.min(dists))
        distances = np.array(distances)
        if distances.max() == distances.min():
            return np.zeros_like(distances)
        scores = (distances - distances.min()) / (distances.max() - distances.min() + 1e-9)
        return scores


class EnsembleDetector:
    def __init__(self, threshold=0.7, weights=None):
        if weights is None:
            weights = {'isolation_forest': 0.4, 'autoencoder': 0.3, 'clustering': 0.3}
        self.weights = weights
        self.threshold = threshold
        self.isolation_forest = IsolationForest(contamination=0.05, random_state=42)
        self.autoencoder = AutoencoderAnomalyDetector()
        self.clustering = ClusteringAnomalyDetector()
        self.isolation_forest_trained = False
        self.autoencoder_trained = False
        self.clustering_trained = False
        self.feature_names_ = None

    def fit(self, X):
        if isinstance(X, pd.DataFrame):
            self.feature_names_ = X.columns.tolist()
            X = X.values
        else:
            self.feature_names_ = [f"feature_{i}" for i in range(X.shape[1])]
        self.isolation_forest.fit(X)
        self.isolation_forest_trained = True
        self.autoencoder.fit(X)
        self.autoencoder_trained = True
        self.clustering.fit(X)
        self.clustering_trained = True

    def predict(self, X):
        if isinstance(X, pd.DataFrame):
            X = X.values
        raw_scores = self.isolation_forest.decision_function(X)
        is_scores = 1.0 - ((raw_scores - raw_scores.min()) / (raw_scores.max() - raw_scores.min() + 1e-9))
        ae_scores = self.autoencoder.predict(X)
        cl_scores = self.clustering.predict(X)
        ensemble = (
            self.weights['isolation_forest'] * is_scores
            + self.weights['autoencoder'] * ae_scores
            + self.weights['clustering'] * cl_scores
        )
        return {
            'isolation_forest_score': is_scores.tolist(),
            'autoencoder_score': ae_scores.tolist(),
            'clustering_score': cl_scores.tolist(),
            'ensemble_score': ensemble.tolist(),
            'is_anomaly': (ensemble > self.threshold).tolist(),
        }

    def get_feature_importance(self):
        if self.feature_names_ is None:
            return {}
        return {
            'features': self.feature_names_,
            'description': 'Isolation Forest contributes 40%, Autoencoder 30%, Clustering 30%.',
        }

    def get_model_status(self):
        return {
            'isolation_forest': 'trained' if self.isolation_forest_trained else 'untrained',
            'autoencoder': 'trained' if self.autoencoder_trained else 'untrained',
            'clustering': 'trained' if self.clustering_trained else 'untrained',
            'weights': self.weights,
            'threshold': self.threshold,
        }
