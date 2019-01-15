import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError

from app import Article, db
import calendar

import locale

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

path_to_chromedriver = '/usr/lib/chromium-browser/chromedriver'
path_to_firefoxdirver = '/usr/local/bin/geckodriver/geckodriver'

BASEURL = 'https://www.cartacapital.com.br/'
SECTION_URL = 'Politica/'


def getArticles(articles, website, section):
    for a in articles:
        atag = a.find_element_by_xpath('//h3/a')
        title = atag.text
        print(title)
        link = atag.get_attribute("href")
        subtitle = a.find_element_by_css_selector('p.eltdf-post-excerpt').text

        pdatetime = a.find_element_by_xpath("//div[contains(@class, 'eltdf-post-info-date')]/a").text.split(' ')
        day = pdatetime[0]
        month_abrev = pdatetime[1][:3].lower()
        month_number = list(calendar.month_abbr).index(month_abrev)
        year = pdatetime[2]
        pdate = '{0}/{1}/{2}'.format(day, month_number, year)
        ptime = None
        author = a.find_element_by_xpath("//div[contains(@class, 'eltdf-post-info-author')]/a").text

        firefox.get(link)
        # firefox.execute_script("document.getElementsByClassName('rp-de-texto').innerHTML = '<div></div>';")
        content = firefox.find_element_by_xpath("//div[contains(@class, 'eltdf-post-text-inner')]").text
        index = content.find('Muito obrigado por ter chegado até aqui...')
        content = content[:index - 1]
        articl = Article(website=website, title=title, subtitle=subtitle, author=author, url=link, content=content,
                         section=section, publish_date=pdate, publish_time=ptime)
        db.session.add(articl)

        try:
            db.session.commit()
            print('success')
        except IntegrityError:
            # db.rollback()
            print('article already existed')
            db.session.rollback()
            pass


def getArticlesAjax(articles, website, section, n):
    for a in articles:
        h3title = a.find('h3')
        atag = h3title.a
        link = atag.attrs['href']
        title = atag.text
        subtitle = a.find("p", {"class": 'eltdf-post-excerpt'}).text
        pdatetime = a.find("div", {"class": 'eltdf-post-info-date'}).a.text.strip().split(' ')
        day = pdatetime[0]
        month_abrev = pdatetime[1][:3].lower()
        month_number = list(calendar.month_abbr).index(month_abrev)
        year = pdatetime[2]
        pdate = '{0}/{1}/{2}'.format(day, month_number, year)
        ptime = None
        author = a.find("div", {"class": 'eltdf-post-info-author'}).text

        firefox.get(link)
        try:
            content = firefox.find_element_by_xpath("//div[contains(@class, 'eltdf-post-text-inner')]").text
        except NoSuchElementException:
            content = ''
            continue

        index = content.find('Muito obrigado por ter chegado até aqui...')
        content = content[:index - 1]
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
chrome.set_window_position(-2000, 0)
firefox = webdriver.Firefox()
firefox.set_window_position(-2000, 0)
chrome.get(BASEURL + SECTION_URL)
website = 'carta capital'
section = 'politica'
# articles = chrome.find_elements_by_xpath(
#     "//div[contains(@class, 'eltdf-bnl-inner')]/div[contains(@class, 'eltdf-pt-three-item')]")
# getArticles(articles, website, section)

for l in range(836, 1300):
    data = 'next_page={0}&max_pages=1290&paged={0}&pagination_type=load-more&display_pagination=yes&excerpt_length=70&display_excerpt=yes&display_comments=no&display_author=yes&display_category=no&display_date=yes&thumb_image_size=full&sort=latest&post_not_in=0000&category_id=412&column_number=1&number_of_posts=6&parallax_effect=no&base=eltdf_post_layout_three&action=readanddigest_list_ajax'
    cookies_list = chrome.get_cookies()
    cookies_dict = {}
    for cookie in cookies_list:
        cookies_dict[cookie['name']] = cookie['value']

    headers = {'content-type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Connection': 'keep-alive', 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:64.0) Gecko/20100101 Firefox/64.0'}
    response = requests.post('https://www.cartacapital.com.br/wp-admin/admin-ajax.php', cookies=cookies_dict, headers=headers, data=data.format(l))

    soup = BeautifulSoup(response.json()['html'])
    articlesAjax = soup.findAll("div", {"class": "eltdf-pt-three-item"})
    getArticlesAjax(articlesAjax, website, section, l)


