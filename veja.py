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

BASEURL = 'https://www.istoedinheiro.com.br/'
SECTION_URL = 'categoria/economia/politica/'

chrome = None
website = 'veja'
section = 'blog_augusto_nunes'


def getArticlesAjax(firefox, articles, website, section, n):
    # firefox = webdriver.Firefox()

    for a in articles:
        listitem = a.find("span", {"class": 'list-item-title'})
        title = listitem.text
        link = listitem.find('a').attrs['href']

        pdatetime = a.find("span", {"class": 'list-date-description'}).text.split(',')
        pdatestr = pdatetime[0].split(' ')
        day = pdatestr[0]
        month_abrev = pdatestr[1][:3].lower()
        month_number = list(calendar.month_abbr).index(month_abrev)
        year = pdatestr[2]
        pdate = '{0}/{1}/{2}'.format(day, month_number, year)
        ptime = pdatetime[1].replace('h', ':')

        successful = False
        tries = 0

        while not successful:
            print(link)
            try:
                firefox.get(link)
            except:
                print('timeout. page did not load: ' + link)
                sleep(900 * tries)  # sleep for one day
                tries = tries + 1
                if tries == 2:
                    break
                else:
                    continue

            successful = True

        if not successful:
            continue

        author = firefox.find_element_by_xpath("//div[@class='article-author']/span").text
        subtitle = firefox.find_element_by_xpath("//h2[@class='article-subtitle']").text
        content = firefox.find_element_by_xpath("//section[@class='article-content']").text


        articl = Article(website=website, title=title, subtitle=subtitle, author=author, url=link, content=content,
                         publish_date=pdate, publish_time=ptime)

        db.session.add(articl)

        try:
            db.session.commit()
            print('success: {0}'.format(n))
        except:
            print('article already existed')
            db.session.rollback()
            pass


def scrapy(url, urlajax, urllogin):
    chrome = webdriver.Chrome(path_to_chromedriver)
    chrome.get(urllogin)
    cookies_list = chrome.get_cookies()
    cookies_dict = {}
    for cookie in cookies_list:
        cookies_dict[cookie['name']] = cookie['value']

    for l in range(497, 1203):
        data = 'action=infinite_scroll&page={0}&currentday=19.01.19&order=DESC&scripts%5B%5D=jquery-core&scripts%5B%5D=jquery-migrate&scripts%5B%5D=jquery&scripts%5B%5D=mobile-useragent-info&scripts%5B%5D=postmessage&scripts%5B%5D=jquery_inview&scripts%5B%5D=jetpack_resize&scripts%5B%5D=filtros-receitas-scripts&scripts%5B%5D=ingredientes-ads&scripts%5B%5D=filter-receitas&scripts%5B%5D=r-login&scripts%5B%5D=abril_piano&scripts%5B%5D=abril_tinypass&scripts%5B%5D=mustache-js&scripts%5B%5D=widget-top-highlight-js&scripts%5B%5D=widget-top-highlight-swiper-js&scripts%5B%5D=spin&scripts%5B%5D=jquery.spin&scripts%5B%5D=sendinblue-config&scripts%5B%5D=sendinblue-validation&scripts%5B%5D=devicepx&scripts%5B%5D=jetpack_likes_queuehandler&scripts%5B%5D=the-neverending-homepage&scripts%5B%5D=%2Fjs%2Fvendor%2Fjquery.min.js&scripts%5B%5D=%2Fjs%2Fvendor%2Fjquery.appear.js&scripts%5B%5D=%2Fjs%2Fvendor%2Fjquery.flexslider-min.js&scripts%5B%5D=%2Fjs%2Fvendor%2Flazysizes.js&scripts%5B%5D=%2Fjs%2Fvendor%2Fphotoswipe.min.js&scripts%5B%5D=%2Fjs%2Fvendor%2Fphotoswipe-ui-default.min.js&scripts%5B%5D=%2Fjs%2Fvendor%2Fmustache.min.js&scripts%5B%5D=%2Fjs%2Fvideos-abril-call-player.js&scripts%5B%5D=%2Fjs%2Fvideos-abril-player-vars.js&scripts%5B%5D=%2Fjs%2Fvideos-abril-call-sambatech.js&scripts%5B%5D=%2Fjs%2Fapplication.min.js&scripts%5B%5D=%2Fjs%2Fvendor%2Fjquery.lazysizes.min.js&scripts%5B%5D=%2Fjs%2Fvendor%2Fjquery.magnific-popup.min.js&scripts%5B%5D=%2Fjs%2Fgallery.min.js&scripts%5B%5D=https%3A%2F%2Fs1.wp.com%2Fwp-content%2Fthemes%2Fvip%2Fabril-id%2Fjs%2FabrID.js&scripts%5B%5D=%2F%2Fstatic.chartbeat.com%2Fjs%2Fchartbeat_mab.js&scripts%5B%5D=%2F%2Fstatic.chartbeat.com%2Fjs%2Fchartbeat.js&scripts%5B%5D=https%3A%2F%2Fs2.wp.com%2Fwp-content%2Fthemes%2Fvip%2Fabril-master%2Fjs%2Fchartbeat-config.js&scripts%5B%5D=wpcom-vip-analytics&scripts%5B%5D=veja-application-js&scripts%5B%5D=wpcom-masterbar-js&scripts%5B%5D=wpcom-masterbar-tracks-js&scripts%5B%5D=swfobject&scripts%5B%5D=videopress&scripts%5B%5D=jetpack-carousel&scripts%5B%5D=twitter-widgets&scripts%5B%5D=twitter-widgets-infinity&scripts%5B%5D=twitter-widgets-pending&scripts%5B%5D=tiled-gallery&scripts%5B%5D=piano_script_paywall&styles%5B%5D=wpcom-smileys&styles%5B%5D=jetpack_likes&styles%5B%5D=the-neverending-homepage&styles%5B%5D=&styles%5B%5D=wp-block-library&styles%5B%5D=jetpack-email-subscribe&styles%5B%5D=wpcom-core-compat-playlist-styles&styles%5B%5D=mp6hacks&styles%5B%5D=wpcom-bbpress2-staff-css&styles%5B%5D=filtros-receitas-styles&styles%5B%5D=abril-releases-css&styles%5B%5D=abrilID-comments-style&styles%5B%5D=aalb_basics_css&styles%5B%5D=abril_piano_css&styles%5B%5D=jetpack-widget-social-icons-styles&styles%5B%5D=abril-releases-widget-css&styles%5B%5D=widget-top-highlight-swiper-css&styles%5B%5D=noticons&styles%5B%5D=geo-location-flair&styles%5B%5D=reblogging&styles%5B%5D=pages_styles&styles%5B%5D=wp-master-theme-style&styles%5B%5D=h4-global&styles%5B%5D=google-fonts&styles%5B%5D=magnific-popup&styles%5B%5D=jetpack-carousel&styles%5B%5D=tiled-gallery&styles%5B%5D=jetpack-carousel-ie8fix&query_args%5Bblogs%5D=augusto-nunes&query_args%5Berror%5D=&query_args%5Bm%5D=&query_args%5Bp%5D=0&query_args%5Bpost_parent%5D=&query_args%5Bsubpost%5D=&query_args%5Bsubpost_id%5D=&query_args%5Battachment%5D=&query_args%5Battachment_id%5D=0&query_args%5Bname%5D=&query_args%5Bpagename%5D=&query_args%5Bpage_id%5D=0&query_args%5Bsecond%5D=&query_args%5Bminute%5D=&query_args%5Bhour%5D=&query_args%5Bday%5D=0&query_args%5Bmonthnum%5D=0&query_args%5Byear%5D=0&query_args%5Bw%5D=0&query_args%5Bcategory_name%5D=&query_args%5Btag%5D=&query_args%5Bcat%5D=&query_args%5Btag_id%5D=&query_args%5Bauthor%5D=&query_args%5Bauthor_name%5D=&query_args%5Bfeed%5D=&query_args%5Btb%5D=&query_args%5Bpaged%5D=0&query_args%5Bmeta_key%5D=&query_args%5Bmeta_value%5D=&query_args%5Bpreview%5D=&query_args%5Bs%5D=&query_args%5Bsentence%5D=&query_args%5Btitle%5D=&query_args%5Bfields%5D=&query_args%5Bmenu_order%5D=&query_args%5Bembed%5D=&query_args%5Bposts_per_page%5D=10&query_args%5Bignore_sticky_posts%5D=false&query_args%5Bsuppress_filters%5D=false&query_args%5Bcache_results%5D=false&query_args%5Bupdate_post_term_cache%5D=true&query_args%5Blazy_load_term_meta%5D=true&query_args%5Bupdate_post_meta_cache%5D=true&query_args%5Bpost_type%5D=&query_args%5Bnopaging%5D=false&query_args%5Bcomments_per_page%5D=10&query_args%5Bno_found_rows%5D=false&query_args%5Btaxonomy%5D=blogs&query_args%5Bterm%5D=augusto-nunes&query_args%5Border%5D=DESC&query_args%5Bextra%5D%5Bis_tag%5D=false&query_args%5Bextra%5D%5Bis_category%5D=false&query_args%5Bextra%5D%5Bis_admin%5D=false&last_post_date=2019-01-17+14%3A43%3A01'


        headers = {'content-type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest',
                   'Connection': 'keep-alive',
                   'TE': 'Trailers',
                   'Referer': url,
                   'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:64.0) Gecko/20100101 Firefox/64.0'}
        response = requests.post(urlajax, cookies=cookies_dict,
                                 headers=headers, data=data.format(l))

        soup = BeautifulSoup(response.json()['html'])
        articlesAjax = soup.findAll("div", {"class": "list-item-info"})
        getArticlesAjax(chrome, articlesAjax, website, section, l)


scrapy('https://veja.abril.com.br/blog/augusto-nunes/', 'https://veja.abril.com.br/?infinity=scrolling', 'https://veja.abril.com.br/blog/augusto-nunes/sanatoriogeral-porta-voz-de-ladrao-engaiolado/')
