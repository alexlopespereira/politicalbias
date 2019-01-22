import calendar
from time import sleep

import requests
import selenium
import sqlalchemy
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from sqlalchemy.exc import IntegrityError

from app import Article, db

import locale

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

path_to_chromedriver = '/usr/lib/chromium-browser/chromedriver'
path_to_firefoxdirver = '/usr/local/bin/geckodriver/geckodriver'

chrome = None



def getArticles(firefox, articles, website, section, n):

    narticles = 0
    for a in articles:
        narticles = narticles + 1
        try:
            entry = a.find_element_by_class_name("entry-content")
            header = entry.find_element_by_tag_name('header')
        except:
            continue

        tagtitle = header.find_element_by_tag_name('h3')
        title = tagtitle.text
        entrydate = header.find_element_by_class_name("entry-date")
        pdatetime = entrydate.text.split(' de ')

        link = tagtitle.find_element_by_tag_name('a').get_attribute("href")
        print(link)
        day = pdatetime[0]
        month_abrev = pdatetime[1][:3].lower()
        month_number = list(calendar.month_abbr).index(month_abrev)
        year = pdatetime[2]
        pdate = '{0}/{1}/{2}'.format(day, month_number, year)
        ptime = None

        subtitle = a.find_element_by_xpath("//div[@class='entry-content']/p").text
        successful = False
        tries = 0

        while not successful:

            try:
                if tries > 0:
                    firefox.refresh()
                    if firefox.find_element_by_xpath("//div[@id='article-text']"):
                        successful = True
                        content = firefox.find_element_by_xpath("//div[@id='article-text']").text
                        break
                firefox.get(link)
                content = firefox.find_element_by_xpath("//div[@id='article-text']").text
            except:
                print('timeout. page did not load: ' + link)
                # firefox.close()
                # firefox.quit()
                # firefox = webdriver.Chrome(path_to_chromedriver)
                sleep(900 * tries)  # sleep for one day
                tries = tries + 1
                if tries == 2:
                    break
                else:
                    continue

            successful = True


        if not successful:
            continue
        try:
            author = firefox.find_element_by_xpath("//em").text
        except:
            author = None
            pass


        if author:
            content = content.replace(author, '')
        articl = Article(website=website, title=title, subtitle=subtitle, author=author, url=link, content=content, publish_date=pdate, publish_time=ptime)

        db.session.add(articl)

        try:
            db.session.commit()
            print('success: {0} - {1}'.format(n, narticles))
        except:
            print('article already existed')
            db.session.rollback()
            pass

    # firefox.close()
    # firefox.quit()


website = 'gazetadopovo'
section = 'blog_rodrigo_constantino'

def scrapy(url, urllogin):
    chrome = webdriver.Chrome(path_to_chromedriver)

    firefox = webdriver.Chrome(path_to_chromedriver)
    firefox.get(urllogin)

    for l in range(300, 1074):
        successful = False
        tries = 0
        while not successful:
            clink = url + 'page/{0}/'.format(l)
            print(clink)
            try:
                chrome.get(clink)
            except selenium.common.exceptions.TimeoutException as e:
                print('timeout. page did not load: ' + clink)
                sleep(900 * tries)  # sleep for one day
                tries = tries + 1
                continue

            successful = True

        articles = chrome.find_elements_by_xpath("//article")
        getArticles(firefox, articles, website, section, l)


scrapy('https://www.gazetadopovo.com.br/rodrigo-constantino/', 'https://www.gazetadopovo.com.br/rodrigo-constantino/artigos/governo-recua-e-suspende-nomeacao-de-diretor-controverso-para-comandar-enem-fez-bem/')
