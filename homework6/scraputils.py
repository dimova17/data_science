import requests
from bs4 import BeautifulSoup
import time


def extract_news(rows):
    """ Extract news from a given web page """
    news_list = []
    
    for n in range(90):
        if n % 3 == 0:
            news = {}
            news['title'] = rows[n].findAll('a')[1].text
            news['url'] = rows[n].findAll('a')[1]['href']

        elif (n - 1) % 3 == 0:
            news['author'] = rows[n].a.text
            news['points'] = rows[n].span.text[:1]

            if rows[n].findAll('a')[5].text == 'discuss':
                news['comments'] = '0'

            else:
                news['comments'] = rows[n].findAll('a')[5].text[:1]

            news_list.append(news)
    return news_list


def extract_next_page(rows):
    """ Extract next page URL """
    link = rows[-1].a['href']
    return link


def get_news(url, n_pages=1):
    """ Collect news from a given web page """
    news = []
    while n_pages:
        print("Collecting data from page: {}".format(url))
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        rows = soup.table.findAll('table')[1].findAll('tr')
        news_list = extract_news(rows)
        next_page = extract_next_page(rows)
        url = "https://news.ycombinator.com/" + next_page
        news.extend(news_list)
        n_pages -= 1
        time.sleep(3)

    return news


if __name__ == "__main__":
    n = get_news('https://news.ycombinator.com/newest', 2)
    print(n[:10])

