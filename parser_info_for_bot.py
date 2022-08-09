import datetime as dt
import json
import logging
import os
import pickle
import random
import time
from logging.handlers import RotatingFileHandler

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.firefox import GeckoDriverManager
from parser import get_feedback, search_rootId
from parser_articles import get_list_articles

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(BASE_DIR, '../logs/')
log_file = os.path.join(BASE_DIR, '../logs/pars_article_table.log')
console_handler = logging.StreamHandler()
file_handler = RotatingFileHandler(
    log_file,
    maxBytes=100000,
    backupCount=3,
    encoding='utf-8'
)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s, %(levelname)s, %(message)s',
    handlers=(
        file_handler,
        console_handler
    )
)

dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
load_dotenv('.env ')
SPREADSHEET_OPPONENT = os.getenv('SPREADSHEET_OPPONENT')
GH_TOKEN = os.getenv('GH_TOKEN')
SPREADSHEET_ID_ARTICLE = os.getenv('SPREADSHEET_ID_ARTICLE')


def get_info(url, article, month, list_review):
    dict_rev = {}
    len_list = len(list_review)
    access, all, rating, mean_rating, sum_review, remain_review = 0, 0, 0, 0, 0, ''
    driver.get(url)
    cookies = pickle.load(open(f'cookies_mpboost.py', 'rb'))
    for cookie in cookies:
        driver.add_cookie(cookie)
    time.sleep(5)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    if soup.find_all('table', class_='table'):
        for row in soup.find_all('tr', class_='table__row'):
            row_t = row.get_text().strip()
            for i in list_review:
                if row_t.find(i['review']) != -1:
                    len_list -= 1
                    list_review.remove(i)
            if row_t.find(f'{day} {month}') != -1:
                all += 1
                if row_t.find('Опубликован') != -1:
                    access += 1
    for i in list_review:
        rating += i['rating']
    try:
        mean_rating = round(rating / len(list_review), 1)
        with open(f'/home/lotelove/wb/auto_review/up_feedbacks/list_reviews_opponent_{article}.json',
                  encoding='UTF-8') as f:
            list_review = json.load(f)
        sum_review = len(list_review)
    except:
        pass
    driver.get(f'https://app.mpboost.pro/reviews?search={article}')
    time.sleep(2)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    check_remain = soup.find('div', class_='reviews content')
    for i in check_remain:
        try:
            if (i.get_text().strip()).find('Доступных отзывов нет') != -1:
                remain_review = 0
        except:
            pass
    try:
        for remain in soup.find_all('button', class_='review__btn-new-review btn-'):
            remain_t = remain.get_text().strip()
        for i in remain_t:
            if i.isdigit():
                remain_review += i
    except:
        pass
    dict_rev[article] = access, all, len_list, mean_rating, sum_review, int(remain_review)
    return dict_rev


if __name__ == "__main__":
    all_dict_list = []
    month_list = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
                  'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
    index_month = int(dt.datetime.now().strftime('%#m')) - 1
    day = (dt.datetime.now() - dt.timedelta(days=1)).strftime('%#d')
    date = dt.datetime.now()
    articles_list = get_list_articles(SPREADSHEET_ID_ARTICLE, month = date.strftime('%m'), year = date.strftime('%Y'))
    date = dt.datetime.now()
    last_day = str(dt.datetime.date(dt.datetime.now()) - dt.timedelta(days=1))
    try:
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
        driver.maximize_window()
        for article in articles_list:
            url = f'https://app.mpboost.pro/reviews?search={article}&status=published'
            list_review = get_feedback(search_rootId(int(article)), last_day)
            all_dict_list.append(get_info(url, article, month_list[index_month], list_review))
    except Exception as e:
        print(e)
    finally:
        with open(f'info_for_bot.json', 'w', encoding='UTF-8') as outfile:
            json.dump(all_dict_list, outfile, ensure_ascii=False)
        driver.quit()
