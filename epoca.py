from time import sleep

import requests
import selenium
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError
import re

from app import Article, db
import calendar

import locale

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

path_to_chromedriver = '/usr/lib/chromium-browser/chromedriver'
path_to_firefoxdirver = '/usr/local/bin/geckodriver/geckodriver'

BASEURL = 'https://epoca.globo.com/'
SECTION_URL = 'politica/'

def getArticlesAjax(articles, website, section, n):
    for a in articles:
        if 'autores' in a:
            author = ','.join(map(str, a['autores']))
        else:
            author = None
        link = a['url']
        title = a['titulo']
        tries = 0
        successful = False

        while not successful:
            print(link)
            try:
                firefox.get(link)
            except selenium.common.exceptions.TimeoutException as e:
                print('timeout. page did not load: ' + link)
                sleep(900 * tries)  # sleep for one day
                tries = tries + 1
                continue
            successful = True
        try:
            header = firefox.find_element_by_xpath("//div[contains(@class, 'article__date')]").text
        except NoSuchElementException:
            content = ''
            continue

        hlist = re.split(' ', header)
        pdate = hlist[0]
        ptime = hlist[2]

        content = firefox.find_element_by_xpath("//div[contains(@class, 'article__content-container')]").text.replace('PUBLICIDADE','').lstrip()
        subtitle = firefox.find_element_by_xpath("//div[contains(@class, 'article__subtitle')]").text

        articl = Article(website=website, title=title, subtitle=subtitle, author=author, url=link, content=content,
                         section=section, publish_date=pdate, publish_time=ptime)
        db.session.add(articl)

        try:
            db.session.commit()
            print('success: {0}'.format(n))
        except (IntegrityError, FlushError) as e:
            print('article already existed')
            db.session.rollback()
            pass

chrome = webdriver.Chrome(path_to_chromedriver)
firefox = webdriver.Chrome(path_to_chromedriver)
chrome.get(BASEURL + SECTION_URL)
website = 'epoca'
section = 'politica'

for l in range(56, 1300):
    cookies_list = chrome.get_cookies()
    cookies_dict = {}
    for cookie in cookies_list:
        cookies_dict[cookie['name']] = cookie['value']
    url = 'https://epoca.globo.com/api/v1/vermais/22831804/conteudo.json?pagina={0}&versao=v1&tiposDeConteudo=materia,coluna,fotogaleria,infografico,listaFatos,materiaEmCapitulos,videoGloboCom,votacaoEnriquecida'.format(l)
    headers = {'Accept': '*/*', 'Accept-Language': 'en-US,en;q=0.5', 'Referer': 'https://epoca.globo.com/politica/', 'origin': 'https://epoca.globo.com', 'Connection': 'keep-alive', 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:64.0) Gecko/20100101 Firefox/64.0'}
    response = requests.post(url, cookies=cookies_dict, headers=headers)

    articles = response.json()[0]['conteudos']
    getArticlesAjax(articles, website, section, l)

