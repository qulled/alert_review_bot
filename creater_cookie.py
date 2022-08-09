import os

from dotenv import load_dotenv
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
import pickle
import time


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
load_dotenv('.env ')
GH_TOKEN = os.getenv('GH_TOKEN')

options = Options()
options.add_argument("--start-maximized")
options.add_argument('--headless')
driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")


def get_cookie_DynamicCode(url):
    driver.get(url)
    time.sleep(5)
    phone = driver.find_element(By.XPATH,'/html/body/div[1]/div/div/div[3]/div/div/form/input[1]')
    phone.click()
    phone.send_keys('79104016094')
    time.sleep(1)
    password = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[3]/div/div/form/input[2]')
    password.click()
    password.send_keys('MbZLWg')
    time.sleep(2)
    enter_button = driver.find_element(By.XPATH,'/html/body/div[1]/div/div/div[3]/div/div/form/button')
    enter_button.click()
    time.sleep(2)
    pickle.dump(driver.get_cookies(), open(f'cookies_mpboost.py', 'wb'))
    return driver.quit()


if __name__ == '__main__':
    try:
        get_cookie_DynamicCode('https://app.mpboost.pro/auth')
    except Exception as e:
        print(e)
    finally:
        exit()
