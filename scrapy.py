from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from sqlalchemy.exc import IntegrityError

from app import Article, db

path_to_chromedriver = '/usr/lib/chromium-browser/chromedriver'
path_to_firefoxdirver = '/usr/local/bin/geckodriver/geckodriver'

BASEURL = 'http://www.vermelho.org.br/'
SECTION_URL = 'noticias.php?id_secao=1'


# options = webdriver.ChromeOptions()
# options.add_argument('--ignore-certificate-errors')
# options.add_argument("--test-type")
# options.binary_location = path_to_chromedriver
# driver = webdriver.Chrome(chrome_options=options)

def getArticles(articles, website, n):
    for a in articles:
        try:
            section = a.find_element_by_css_selector('span').text
        except NoSuchElementException:
            section = ''
            continue

        pdatetime = a.find_element_by_css_selector('time').text
        ldatetime = pdatetime.split(' ')
        pdate = ldatetime[0]
        ptime = ldatetime[1].replace('h', ':')
        atag = a.find_element_by_css_selector('a')
        link = atag.get_attribute("href")
        title = atag.get_attribute("title")
        firefox.get(link)
        subtitle_author = firefox.find_element_by_xpath("//article/h2").text.split('\n\n')
        subtitle = subtitle_author[0]
        if len(subtitle_author) > 1:
            author = subtitle_author[1].replace('*', '').replace('Por ', '')
        else:
            author = ''

        content = firefox.find_element_by_xpath("//div[@id='txt_home']").text

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
chrome.set_window_position(-2000,0)
firefox = webdriver.Firefox()
firefox.set_window_position(-2000,0)
# chrome.get(BASEURL + SECTION_URL)
website = 'vermelho'
# articles = chrome.find_elements_by_xpath("//article")
# getArticles(articles)

for l in range(646, 2505):
    chrome.get('http://www.vermelho.org.br/noticias.php?id_secao=1&lista=sintese&pagina={0}'.format(l))
    articles = chrome.find_elements_by_xpath("//article")
    getArticles(articles, website, l)


