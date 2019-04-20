from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from urllib.parse import quote
from pyquery import PyQuery as pq
import pymongo
import time

browser = webdriver.Firefox()
### Firefox headless
# firefox_options = webdriver.FirefoxOptions()
# firefox_options.add_argument('--headless')
# browser = webdriver.Firefox(firefox_options=firefox_options)
wait = WebDriverWait(browser,10)
KEYWORD = 'iphone'
MAX_PAGE = 2

# database
mongo_url = 'localhost'
mongo_db = 'taobao'
mongo_collection = 'products'
client = pymongo.MongoClient(mongo_url)
db = client[mongo_db] #注意是中括号
collection = db[mongo_collection]

def get_one_page(page_num):
    try:
        url = 'https://s.taobao.com/search?q=' + quote(KEYWORD)
        browser.get(url)
        if page_num > 1:
            input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager .form .input')))
            button = browser.find_element_by_css_selector('#mainsrp-pager .form .J_Submit')
            browser.execute_script("arguments[0].scrollIntoView(false);", button)
            submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#mainsrp-pager .form .J_Submit')))
            input.clear()
            input.send_keys(page_num)
            #time.sleep(5)
            submit.click()
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#mainsrp-pager .item.active span'),str(page_num)))
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-itemlist .m-itemlist .items')))
        return (browser.page_source)
    except TimeoutException:
        get_one_page(page_num)

def get_products(html):
    doc = pq(html)
    products = doc('#mainsrp-itemlist .m-itemlist .items .item').items()
    for product in products:
        yield {
            'image': product('.pic img').attr('data-src'),
            'title': product('.pic img').attr('alt'),
            'price': product('.price').text(),
            'deal': product('.deal-cnt').text(),
            'shop': product('.shopname').text(),
            'location': product('.location').text()
        }

def save_to_mongo(product):
    try:
        collection.insert_one(product)
    except Exception:
        print('save failed')

def main():
    for i in range(1,MAX_PAGE+1):
        html = get_one_page(i)
        for product in get_products(html):
            print(product)
            #save_to_mongo(product)
    print('success')

if __name__ == '__main__':
    main()