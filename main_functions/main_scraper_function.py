
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import  WebDriverException
from selenium.webdriver.common.proxy import Proxy, ProxyType

import time
import undetected_chromedriver as uc

from fake_useragent import UserAgent
from bs4 import BeautifulSoup
# F U N C T I O N S
from utils.helpers import print_message, scrollFromToptoBottom, getProductCardListDetail, storingLoggingAs, saveDataToCSV
from utils.product_list_helpers import openNewTabWindow, getTotalPagination
from config.config import BASE_SEARCH_URL_PARAMETER, PROXY_SERVER, KEYWORD_CATEGORY

MAX_RETRY = 10

def eCommerceScrapper(urls = []):
    print_message(f'SCRAPE FUNCTION RUNNING ON PROXY {PROXY_SERVER} . . .', 'success', bold=True)
    proxy = Proxy()
    proxy.proxy_type = ProxyType.MANUAL
    proxy.http_proxy = PROXY_SERVER
    proxy.ssl_proxy = PROXY_SERVER
    ua = UserAgent()
    # services = Service('chromedriver.exe')
    uc_chrome_options = uc.ChromeOptions()
    uc_chrome_options.add_argument(f'user-agent={ua.random}')
    uc_chrome_options.add_argument('--disable-popup-blocking')
    # chrome_options.add_argument(f'--proxy-server=http://{proxy.http_proxy}')
    # chrome_options.add_argument(f'--proxy-server=https://{proxy.ssl_proxy}')
    print_message(f'http: {proxy.http_proxy}, ssl: {proxy.ssl_proxy}', 'info', True)

    time.sleep(10)
    driver = uc.Chrome(options=uc_chrome_options, use_subprocess=False)
    print_message(f'setting up driver . . .', 'info')
    
    driver.get(BASE_SEARCH_URL_PARAMETER)
    time.sleep(20)
    content = driver.page_source
    list_content_soup = BeautifulSoup(content, 'html.parser')
    find_error_el = list_content_soup.find('body', class_='neterror')

    LIST_OF_PRODUCT = []
    if find_error_el is None:
        try:
           
            time.sleep(30)
            print('running without driver error. Start scrolling to footer...')
            [scrolled] = scrollFromToptoBottom(driver, 'footer-first', False, False, 10, 12)
            
            get_total_pagination_of_product_list = getTotalPagination(driver)
            print('scrolled to bottom:', scrolled, 'get_total_pagination_of_product_list', get_total_pagination_of_product_list)
            item_each_page = driver.find_elements(By.XPATH, '//div[@class="Bm3ON"]')
            total_item_per_page = len(item_each_page)
            
            item_counter_page = 0
            product_card_list_detail = getProductCardListDetail(driver)
           
            print('TOTAL URL HAS SAME LENGTH', f'URL: {len(product_card_list_detail)}', f'TOTAL ITEM: {total_item_per_page}' )
            storingLoggingAs('info', f'TOTAL URL HAS SAME LENGTH __ URL: {len(product_card_list_detail)}, __ TOTAL ITEM: {total_item_per_page}')
            if len(product_card_list_detail) == total_item_per_page:
                for product_card_index, product_card_item in enumerate(product_card_list_detail):
                        time.sleep(10)
                        print(f'product_card_index {product_card_index}--{product_card_item["url"]}')
                        storingLoggingAs('info', f'processing {product_card_index} of {len(product_card_list_detail)} url. opening new tab...')
                    
                        openNewTabWindow(driver, product_card_item, LIST_OF_PRODUCT, KEYWORD_CATEGORY, product_card_index, total_item_per_page)
                        print('open new tab succesfully executed')
                        item_counter_page += 1
                        time.sleep(10)   
                        print('done sleep for 10 seconds')

                if len(LIST_OF_PRODUCT) > 0:
                    saveDataToCSV(LIST_OF_PRODUCT, KEYWORD_CATEGORY, 'success')
        except WebDriverException as e:
            print('WebDriverException', e)
            if "ERR_HTTP2_PROTOCOL_ERROR" in str(e):
                print_message(f'Encountered ERR_HTTP2_PROTOCOL_ERROR: {e}', 'error', True)
                if len(LIST_OF_PRODUCT) > 0:
                    saveDataToCSV(LIST_OF_PRODUCT, KEYWORD_CATEGORY, 'error')

                
