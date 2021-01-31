import numpy as np
from collections import Counter
from textblob import TextBlob


def dict_unique_words(str_list, n):
    c = Counter()

    for i in str_list:
        blob = TextBlob(i)
        x = list(blob.words.lemmatize())
        phrases = list(blob.noun_phrases)
        for phr in phrases:
            if phr not in x:
                phrase = ' '.join(phr)
                x.append(phrase)
        ngrams = blob.ngrams(n)
        for gr in ngrams:
            if gr not in x:
                ngram = ' '.join(gr)
                x.append(ngram)
        for w in x:
            c[w] += 1
    unique_words = dict(c)
    return unique_words


class NaiveBayesClassifier:

    def __init__(self, alpha=1, n=2):
        self.alpha = alpha
        self.n = n
        self.examples_cl = []
        self.P_cl_list = []
        self.unique_words_cl = []
        self.prediction = []

    def fit(self, X, y):
        """ Fit Naive Bayes classifier according to X, y. """
        classes = set(y)
        self.labels = list(classes)
        self.unique_words = dict_unique_words(X, self.n)

        while len(self.examples_cl) < len(classes):
            for i in self.labels:
                clas = [X[j] for j in range(len(X)) if y[j] == i]
                self.examples_cl.append(clas)

        for i in range(len(classes)):
            self.P_cl_list.append(len(self.examples_cl[i]) / len(X))
            w_dict = dict_unique_words(self.examples_cl[i], self.n)
            self.unique_words_cl.append(w_dict)
        return self.labels, self.unique_words_cl[0], self.unique_words_cl[1], self.examples_cl, self.P_cl_list

    def predict(self, X):
        """ Perform classification on an array of test vectors X. """

        for example in X:
            P_example_in_class = []
            words = example.split()

            for l in self.labels:
                P_words_in_class = []

                for word in words:
                    if word in self.unique_words_cl[self.labels.index(l)]:
                        n = self.unique_words_cl[self.labels.index(l)][word] + self.alpha

                    else:
                        n = self.alpha
                    g = (sum(self.unique_words_cl[self.labels.index(l)].values()) + self.alpha * len(self.unique_words))
                    P_word = n / g
                    P_words_in_class.append(P_word)

                p = np.log(self.P_cl_list[self.labels.index(l)]) + sum(np.log(P_words_in_class))
                P_example_in_class.append(p)

            c = P_example_in_class.index(np.max(P_example_in_class))
            self.prediction.append(self.labels[c])

        return self.prediction

    def score(self, X_test, y_test):
        """ Returns the mean accuracy on the given test data and labels. """
        y_pr = self.predict(X_test)
        a = 0
        for i in range(len(y_test)):
            if y_pr[i] == y_test[i]:
                a += 1

        return a / len(y_test)

