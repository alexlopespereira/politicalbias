from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from sqlalchemy.exc import IntegrityError

from app import Article, db

path_to_chromedriver = '/usr/lib/chromium-browser/chromedriver'
path_to_firefoxdirver = '/usr/local/bin/geckodriver/geckodriver'

BASEURL = 'https://www.istoedinheiro.com.br/'
SECTION_URL = 'categoria/economia/politica/'


def getArticles(articles, website, section, n):
    for a in articles:
        try:
            atag = a.find_element_by_xpath('//h3/a')
        except NoSuchElementException:
            continue

        title = atag.get_attribute("title")
        link = atag.get_attribute("href")

        pdatetime = a.find_element_by_xpath('//a/time').get_attribute("datetime")
        ldatetime = pdatetime.split(' ')
        pdate = ldatetime[0]
        ptime = ldatetime[1]
        subtitle = a.find_element_by_xpath("//a/p").text

        firefox.get(link)

        author = firefox.find_element_by_xpath("//p[@class='author']/a").text

        content = firefox.find_element_by_xpath("//div[@class='content-section content']").text

        articl = Article(website=website, title=title, subtitle=subtitle, author=author, url=link, content=content, publish_date=pdate, publish_time=ptime)
        db.session.add(articl)

        try:
            db.session.commit()
            print('success: {0}'.format(n))
        except IntegrityError:
            # db.rollback()
            print('article already existed')
            db.session.rollback()
            pass
        #     raise
        # finally:
        #     db.session.close()


chrome = webdriver.Chrome(path_to_chromedriver)
firefox = webdriver.Firefox()
firefox.set_window_position(-2000,0)
# chrome.get(BASEURL + SECTION_URL)
website = 'vermelho'
section = 'politica'
# articles = chrome.find_elements_by_xpath("//article")
# getArticles(articles)

for l in range(1, 1198):
    chrome.get('https://www.istoedinheiro.com.br/categoria/economia/politica/page/{0}/'.format(l))
    articles = chrome.find_elements_by_xpath("//article")
    getArticles(articles, website, section, l)


