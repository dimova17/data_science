from bottle import (
    route, run, template, request, redirect
)
import re
import string
from collections import Counter
from scraputils import get_news
from db import News, session
from bayes import NaiveBayesClassifier


@route('/')
@route("/news")
def news_list():
    s = session()
    rows = s.query(News).filter(News.label == None).all()
    return template('news_template', rows=rows)


@route("/add_label/")
def add_label():
    # 1. Получить значения параметров label и id из GET-запроса
    # 2. Получить запись из БД с соответствующим id (такая запись только одна!)
    # 3. Изменить значение метки записи на значение label
    # 4. Сохранить результат в БД
    s = session()
    news_id = request.query.id
    new_label = request.query.label
    line = s.query(News).filter(News.id == news_id).all()
    line[0].label = new_label

    s.add(line[0])
    s.commit()

    redirect("/news")


@route("/update")
def update_news():
    # 1. Получить данные с новостного сайта
    # 2. Проверить, каких новостей еще нет в БД. Будем считать,
    #    что каждая новость может быть уникально идентифицирована
    #    по совокупности двух значений: заголовка и автора
    # 3. Сохранить в БД те новости, которых там нет
    updates = get_news('https://news.ycombinator.com/newest', n_pages=3)
    s = session()
    for d in updates:
        old = s.query(News).filter(News.title == d['title']).filter(News.author == d['author']).all()
        if not old:
            s.add(News(**d))
    s.commit()

    redirect("/news")


def clean(s):
    p = string.punctuation + '1234567890'
    translator = str.maketrans("", "", p)
    return s.translate(translator)


@route("/classify")
def classify_news():
    # 1. Получить список неразмеченных новостей из БД
    # 2. Получить прогнозы для каждой новости
    # 3. Вывести ранжированную таблицу с новостями

    s = session()
    labeled = s.query(News).filter(News.label != None).all()
    X, y = [], []
    for i in labeled:
        X.append(i.title)
        y.append(i.label)
    X = [clean(x).lower() for x in X]

    model = NaiveBayesClassifier()
    model.fit(X, y)

    no_label = s.query(News).filter(News.label == None).all()
    X_p = []
    for i in no_label:
        X_p.append(i.title)
    X_p = [clean(x).lower() for x in X_p]
    y_predict = model.predict(X_p)

    classified_news = []
    for j in range(len(no_label)):
        no_label[j].label = y_predict[j]
        if y_predict[j] == 'good':
            classified_news.append(no_label[j])

    return template('news_recommendations', rows=classified_news)




if __name__ == "__main__":
    run(host="localhost", port=8080)

