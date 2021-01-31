import numpy as np


class KMeans:
    def __init__(self, n_clusters):
        self.n_clusters = n_clusters
        pass

    def fit(self, X):
        m = X.shape[0]
        self.centroids = X[np.random.choice(m, self.n_clusters, replace=False),]
        self.cluster = np.zeros(m)

        while True:
            for i in range(m):
                eucl = np.linalg.norm(X[i,] - self.centroids, axis=1)
                self.cluster[i] = eucl.argmin()

            centr_prev = self.centroids.copy()

            for k in range(self.n_clusters):
                self.centroids[k] = (1.0 / X[self.cluster == k,].shape[0]) * X[self.cluster == k,].sum(axis=0)

            if (centr_prev == self.centroids).all():
                break

    def predict(self, y):
        cluster = np.zeros(len(y))
        for i in range(len(y)):
            eucl = np.linalg.norm(y[i,] - self.centroids, axis=1)
            cluster[i] = eucl.argmin()
        return cluster
