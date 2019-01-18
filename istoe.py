from time import sleep

import selenium
import sqlalchemy
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from sqlalchemy.exc import IntegrityError

from app import Article, db

path_to_chromedriver = '/usr/lib/chromium-browser/chromedriver'
path_to_firefoxdirver = '/usr/local/bin/geckodriver/geckodriver'

BASEURL = 'https://www.istoedinheiro.com.br/'
SECTION_URL = 'categoria/economia/politica/'

chrome = None
website = 'istoe'
section = 'politica'

def getArticles(articles, website, section, n):
    firefox = webdriver.Chrome(path_to_chromedriver)

    for a in articles:
        try:
            htag = a.find_element_by_tag_name("h3")
            atag = htag.find_elements_by_tag_name("a")
        except NoSuchElementException:
            continue

        title = atag[0].text
        link = atag[0].get_attribute("href")

        pdatetime = a.find_element_by_xpath('//a/time').get_attribute("datetime")
        ldatetime = pdatetime.split(' ')
        pdate = ldatetime[0]
        ptime = ldatetime[1]
        subtitle = a.find_element_by_xpath("//a/p").text
        successful = False
        tries = 0

        while not successful:
            print(link)
            try:
                firefox.get(link)
                author = firefox.find_element_by_xpath("//p[@class='author']/a").text
            except:
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


        content = firefox.find_element_by_xpath("//div[@class='content-section content']").text

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



for l in range(143, 1198):
    successful = False
    tries = 0
    while not successful:
        if chrome:
            chrome.close()
            chrome.quit()
        chrome = webdriver.Chrome(path_to_chromedriver)
        clink = 'https://www.istoedinheiro.com.br/categoria/economia/politica/page/{0}/'.format(l)
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

    articles = chrome.find_elements_by_xpath("//article[contains(@class, 'thumb')]")
    getArticles(articles, website, section, l)


