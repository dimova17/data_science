from db import News
from scraputils import get_news
from db import session

s = session()
news = get_news('https://news.ycombinator.com/newest', n_pages=10)

for n in news:
    s.add(News(**n))
s.commit()
