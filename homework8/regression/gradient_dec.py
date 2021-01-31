import numpy as np


class GDRegressor:
    def __init__(self, alpha=0.05, max_iter=100):
        self.alpha = alpha
        self.n_iter = max_iter
        pass

    def fit(self, X_train, y_train):
        m = len(y_train)
        X = X_train.copy()
        X.insert(0, "Ones", np.ones(len(X)))
        theta = np.zeros(X.shape[1])

        for i in range(self.n_iter):
            new_th = (1 / m) * (np.dot(X.transpose(), (np.dot(X, theta) - y_train)))
            theta = theta - self.alpha * new_th

        self.coef_ = theta[1]  # вектор оценок для θi
        self.intercept_ = theta[0]  # оцененное значение для θ0

    def predict(self, X_test):
        """ Метод predict возвращает вектор прогнозов для новых данных."""
        y_predict = self.intercept_ + self.coef_ * X_test

        return y_predict


def rmse(y_hat, y):
    """ Root mean squared error """
    m = len(y)
    num = 0
    for i in range(m):
        a = (y_hat.iloc[i] - y.iloc[i]) ** 2
        num += a
    Rmse = np.sqrt(num / m)
    return Rmse


def r_squared(y_hat, y):
    """ R-squared score = Коэффициент детерминации"""
    y_mean = np.sum(y) * (1 / len(y))
    rss = 0
    tss = 0
    for i in range(len(y)):
        a = (y.iloc[i] - y_hat.iloc[i]) ** 2
        b = (y.iloc[i] - y_mean) ** 2
        rss += a
        tss += b
    r_sqr = 1 - rss / tss
    return r_sqr