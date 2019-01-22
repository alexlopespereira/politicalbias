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
        h2 = a.find_element_by_class_name("entry-title")
        h2a = h2.find_element_by_tag_name("a")
        title = h2a.text
        link = h2a.get_attribute("href")
        entrymeta = a.find_element_by_xpath("//div[@class='entry-meta']")
        pdatetime = entrymeta.find_element_by_class_name('datetime').text.replace("'", '').split(' ')
        day = pdatetime[0]
        month_abrev = pdatetime[1][:3].lower()
        month_number = list(calendar.month_abbr).index(month_abrev)
        year = pdatetime[2]
        pdate = '{0}/{1}/{2}'.format(day, month_number, year)
        ptime = None

        author = entrymeta.find_element_by_class_name('author').text

        subtitle = a.find_element_by_xpath("//div[@class='entry-content']/p").text
        successful = False
        tries = 0

        while not successful:
            print(link)
            try:
                if tries > 0:
                    firefox.refresh()
                    if firefox.find_element_by_xpath("//article']"):
                        successful = True
                        content = firefox.find_element_by_xpath("//div[@class='entry-content']").text
                        break
                firefox.get(link)
                content = firefox.find_element_by_xpath("//div[@class='entry-content']").text
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

        articl = Article(website=website, title=title, subtitle=subtitle, author=author, url=link, content=content, publish_date=pdate, publish_time=ptime, section=section)

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


website = 'institutoliberal'
section = 'blog'

def scrapy(url):
    chrome = webdriver.Chrome(path_to_chromedriver)

    firefox = webdriver.Chrome(path_to_chromedriver)
    # firefox.get(url)

    for l in range(189, 190):
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


scrapy('https://www.institutoliberal.org.br/blog/')
