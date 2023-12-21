import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.action_chains import ActionChains
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
# F U N C T I O N S
from utils.helpers import print_message, scrollFromToptoBottom, getProductCardListDetail, storingLoggingAs, saveDataToCSV
from utils.product_list_helpers import openNewTabWindow
from config.config import BASE_SEARCH_URL_PARAMETER, PROXY_SERVER, KEYWORD_CATEGORY
from main_functions.product_details.get_main_product_detail import getProductDetail

MAX_RETRY = 10

def eCommerceScrapper(urls = []):
    print_message(f'SCRAPE FUNCTION RUNNING ON PROXY {PROXY_SERVER} . . .', 'success', bold=True)
    proxy = Proxy()
    proxy.proxy_type = ProxyType.MANUAL
    proxy.http_proxy = PROXY_SERVER
    proxy.ssl_proxy = PROXY_SERVER
    ua = UserAgent()
    chrome_options = webdriver.ChromeOptions()
    services = Service('chromedriver.exe')
    chrome_options.add_argument(f'user-agent={ua.random}')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36')
    # chrome_options.add_argument(f'--proxy-server=http://{proxy.http_proxy}')
    # chrome_options.add_argument(f'--proxy-server=https://{proxy.ssl_proxy}')
    print_message(f'http: {proxy.http_proxy}, ssl: {proxy.ssl_proxy}', 'info', True)

    print_message('argument added', 'info')
    time.sleep(10)
    driver = webdriver.Chrome(service=services, options=chrome_options)
    print_message(f'setting up driver . . .', 'info')

    driver.get(BASE_SEARCH_URL_PARAMETER)
    content = driver.page_source
    list_content_soup = BeautifulSoup(content, 'html.parser')
    find_error_el = list_content_soup.find('body', class_='neterror')

    current_datetime = datetime.now()
    formatted_timestamp = current_datetime.strftime("%Y%m%d%H%M%S")

    print('formatted_timestamp', formatted_timestamp)
    LIST_OF_PRODUCT = []
    if find_error_el is None:
        try:
            time.sleep(60)
            print('running without driver error. Start scrolling to footer')
            [scrolled] = scrollFromToptoBottom(driver, 'footer-first', False, True, 10)
            print('scrolled to bottom:', scrolled)
            wait = WebDriverWait(driver, 120)

            # container class Ms6aG
            
            wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="Ms6aG"]')))
            print('waiting for presence of element done')
            
            all_item_each_page = driver.find_elements(By.XPATH, '//div[@class="Ms6aG"]')
            total_item_per_page = len(all_item_each_page)

            item_counter_page = 0
            product_card_list_detail = getProductCardListDetail(driver)
            print('total_item_per_page', total_item_per_page)
            print('TOTAL URL HAS SAME LENGTH', f'URL: {len(product_card_list_detail)}', f'TOTAL ITEM: {total_item_per_page}' )
            storingLoggingAs('info', f'TOTAL URL HAS SAME LENGTH __ URL: {len(product_card_list_detail)}, __ TOTAL ITEM: {total_item_per_page}')
            if len(product_card_list_detail) == total_item_per_page:
                for card_list_item_index, card_list_item in enumerate(product_card_list_detail):
                        time.sleep(10)
                        print(f'card_list_item_index {card_list_item_index}. {card_list_item.url}')
                        storingLoggingAs('info', f'processing {card_list_item_index} of {len(product_card_list_detail)} url. opening new tab...')
                    
                        openNewTabWindow(driver, card_list_item, LIST_OF_PRODUCT, KEYWORD_CATEGORY)
                        item_counter_page += 1
                        time.sleep(10)   

                if len(LIST_OF_PRODUCT) > 0:
                    saveDataToCSV(LIST_OF_PRODUCT, KEYWORD_CATEGORY, 'success')
                    
        except WebDriverException as e:
            if "ERR_HTTP2_PROTOCOL_ERROR" in str(e):
                print_message(f'Encountered ERR_HTTP2_PROTOCOL_ERROR: {e}', 'error', True)
                if len(LIST_OF_PRODUCT) > 0:
                    saveDataToCSV(LIST_OF_PRODUCT, KEYWORD_CATEGORY, 'error')

                
