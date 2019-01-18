from time import sleep

import selenium
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from sqlalchemy.exc import IntegrityError

from app import Article, db

path_to_chromedriver = '/usr/lib/chromium-browser/chromedriver'
path_to_firefoxdirver = '/usr/local/bin/geckodriver/geckodriver'

BASEURL = 'http://www.vermelho.org.br/'
SECTION_URL = 'noticias.php?id_secao=1'
chrome = None
website = 'vermelho'


def getArticles(articles, website, n):
    firefox = webdriver.Chrome(path_to_chromedriver)

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
        successful = False
        tries = 0
        while not successful:
            print(link)
            try:
                firefox.get(link)
                subtitle_author = firefox.find_element_by_xpath("//article/h2").text.split('\n\n')
            except:
                # print str(e)
                print('timeout. page did not load: ' + link)
                firefox.close()
                firefox.quit()
                firefox = webdriver.Chrome(path_to_chromedriver)
                sleep(900 * tries)  # sleep for one day
                tries = tries + 1
                if tries == 2:
                    break
                else:
                    continue

            successful = True

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
        except:
            print('article already existed')
            db.session.rollback()
            pass

    firefox.close()
    firefox.quit()


for l in range(1230, 2505):
    successful = False
    tries = 0
    while not successful:
        if chrome:
            chrome.close()
            chrome.quit()
        chrome = webdriver.Chrome(path_to_chromedriver)

        clink = 'http://www.vermelho.org.br/noticias.php?id_secao=1&lista=sintese&pagina={0}'.format(l)
        print(clink)
        try:
            chrome.get(clink)
        except selenium.common.exceptions.TimeoutException as e:
            print('timeout. page did not load: ' + clink)
            sleep(900 * tries)  # sleep for one day
            tries = tries + 1
            if tries == 2:
                break
            else:
                continue

        successful = True

    articles = chrome.find_elements_by_xpath("//article[contains(@class, 'categoria_item')]")
    getArticles(articles, website, l)


