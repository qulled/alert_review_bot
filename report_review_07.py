import json
import logging
import time
from typing import List, NamedTuple
from google.oauth2 import service_account
import os
from dotenv import load_dotenv
import datetime as dt

# import telegram
from googleapiclient import discovery

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CREDENTIALS_FILE = '../credentials_service.json'
credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_FILE)
service = discovery.build('sheets', 'v4', credentials=credentials)

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID', None)
GROUP_ID = os.getenv('GROUP_ID', None)
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN_FOR_REPORTS']
ID_FOR_NOTIFICATION = 
bot = telegram.Bot(token=TELEGRAM_TOKEN)
SPREADSHEET_ID_ARTICLE= os.environ['SPREADSHEET_ID_ARTICLE']


class ReviewInfo(NamedTuple):
    wb_art: int
    access_review: int
    name : str
    all_review: int
    len_review_list: int
    mean_rating: int
    balance_review: int
    remain_review: int


def get_all_rows(day, month, spreadsheet_id, year=2022):
    range_name = f'{month}.{year}'
    credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_FILE)
    service = discovery.build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID_ARTICLE,
                                range=f'{range_name}!A:GS', majorDimension='ROWS').execute()

    values = result.get('values', [])
    return values


def get_int_value_or_0(row: list, postion: int) -> int:
    try:
        value = int(row[postion].split(',')[0])
    except:
        value = 0
    return value


def get_articles_review(day: str, month: str, spreadsheet_id: str) -> List[ReviewInfo]:
    dict_review = {}
    START_POSITION_FOR_PLACE = 14
    position_for_place = START_POSITION_FOR_PLACE + (int(day) - 1) * 6
    rows = get_all_rows(day, month, spreadsheet_id)
    with open('info_for_bot.json', encoding='UTF-8') as f:
        list_reviews = json.load(f)
    for row in rows:
        try:
            if '??????????????????????' in row[2].upper():
                # print(row[2])
                article = row[5]
                wb_art = int(row[6])
                name = row[3].strip().replace("\n", "")
                for i in list_reviews:
                    lst = i.get(str(wb_art))
                    if lst is not None:
                        access_review = lst[0]
                        all_review = lst[1]
                        len_review_list = lst[2]
                        mean_rating = lst[3]
                        balance_review = lst[4]
                        remain_review = lst[5]

                        dict_review[article] = ReviewInfo(
                            wb_art,
                            access_review,
                            name,
                            all_review,
                            len_review_list,
                            mean_rating,
                            balance_review,
                            remain_review
                        )

        except Exception as e:
            logging.error(e, exc_info=True)
    return dict_review



def format_message(articles_info: List[ReviewInfo], date):
    msg = ''
    articles_info = get_articles_review(day, month, spreadsheet_id='1LMqyN5w81xnRfvNf0CE75ozH7zMcTLhvYiNjTxHDURo')
    for article, info in articles_info.items():
        info: ReviewInfo
        wb_art = info.wb_art
        name = info.name
        access_review = info.access_review
        all_review= info.all_review
        len_review_list=info.len_review_list
        mean_rating = info.mean_rating
        balance_review = info.balance_review
        remain_review = info.remain_review
        msg += (
            f'<b>{article}</b> \n <a href="https://www.wildberries.ru/catalog/{wb_art}/detail.aspx?targetUrl=SP">{name}</a>\n <code>{wb_art}</code>\n\n'
            f' ??? ?????????? ?????????????? {len_review_list} \n'
            f' ??? ?????????????? ?????? ???? ???????? {mean_rating} \n \n'
            f' ??? ?????????? ?????????????? = {all_review} \n'
            f' ??? ?????? ???????????????? ???? = {access_review}\n\n'
            f' ??? ?????????????? ?? ???????????? ?????????????? = {balance_review} \n'
            f' ??? ?????????????? ?????????????? ???? ???????????????? ?? ???? ???????? = {remain_review} \n'
            )
        msg += '\n'
    return msg



def send_report_by_day_review(day: int, month: int):
    msg = ''
    all_rev = 0
    access_rev = 0
    msg = f'{dt.datetime.now().strftime("%R %e.%m")}' + f'\n<u><b>?????????? ???? ??????????????</b></u>\n'
    print(msg)
    bot.send_message(GROUP_ID, msg, parse_mode='HTML', disable_web_page_preview=True)
    articles_info = get_articles_review(day, month, spreadsheet_id='1LMqyN5w81xnRfvNf0CE75ozH7zMcTLhvYiNjTxHDURo')
    for article, info in articles_info.items():
        info: ReviewInfo
        wb_art = info.wb_art
        name = info.name
        access_review = info.access_review
        all_review = info.all_review
        len_review_list = info.len_review_list
        mean_rating = info.mean_rating
        balance_review = info.balance_review
        remain_review = info.remain_review
        all_rev += info.all_review
        access_rev += info.access_review
        
        msg = (
            f'<b>{article}</b> \n <a href="https://www.wildberries.ru/catalog/{wb_art}/detail.aspx?targetUrl=SP">{name}</a>\n <code>{wb_art}</code>\n\n'
            f' ??? ?????????? ?????????????? {len_review_list} \n'
            f' ??? ?????????????? ?????? ???? ???????? {mean_rating} \n \n'
            f' ??? ?????????? ?????????????? = {all_review} \n'
            f' ??? ?????? ???????????????? ???? = {access_review}\n\n'
            f' ??? ?????????????? ?? ???????????? ?????????????? = {balance_review} \n'
            f' ??? ?????????????? ?????????????? ???? ???????????????? ?? ???? ???????? = {remain_review} \n'
        )
        msg += '\n'
        print(msg)
        bot.send_message(GROUP_ID, msg, parse_mode='HTML', disable_web_page_preview=True)
        time.sleep(2)
        all_rev += info.all_review
        access_rev += info.access_review
    for article, info in articles_info.items():
        info: ReviewInfo
        wb_art = info.wb_art
        name = info.name
        access_review = info.access_review
        all_review = info.all_review
        len_review_list = info.len_review_list
        mean_rating = info.mean_rating
        balance_review = info.balance_review
        remain_review = info.remain_review
        all_rev += info.all_review
        access_rev += info.access_review
    msg = f'??????????\n???????????????????? {all_rev}\n???????????? {access_rev}'
    print(msg)
    bot.send_message(GROUP_ID, msg, parse_mode='HTML', disable_web_page_preview=True)



if __name__ == '__main__':
    day =int((dt.datetime.now()-dt.timedelta(days=1)).strftime('%d'))
    month =(dt.datetime.now()-dt.timedelta(days=1)).strftime('%m')
    send_report_by_day_review(day, month)
