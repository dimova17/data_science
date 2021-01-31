import numpy as np
import pandas as pd


class LogisticRegression:
    def __init__(self, alpha=0.001, max_iter=5000):
        self.alpha = alpha
        self.max_iter = max_iter
        pass

    def fit(self, X_train, y_train):

        m = len(y_train)
        X = X_train.copy()
        X = np.insert(X_train, 0, 1, axis=1)

        theta = np.zeros(X.shape[1])

        for n in range(self.max_iter):
            z = np.dot(theta, X.T)
            sigma = 1 / (1 + np.exp(-z))
            J_der = np.dot((sigma - y_train), X)

            theta = theta - self.alpha * (1 / m) * J_der  # обновление весов

        self.intercept = theta[0]
        self.coef = theta[1:]

    def predict(self, X_test):
        prediction = []
        for i in X_test:
            z = self.intercept + np.sum(i * self.coef)
            sigma = 1 / (1 + np.exp(-z))

            if sigma >= 0.5:
                prediction.append(1)
            else:
                prediction.append(0)

        return prediction

    def predict_proba(self, X_test):
        prob = []

        for i in X_test:
            z = self.intercept + np.sum(i * self.coef)
            sigma = 1 / (1 + np.exp(-z))
            prob.append((sigma, 1 - sigma))
        return prob
