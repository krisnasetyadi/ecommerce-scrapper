import logging
from logging.handlers import TimedRotatingFileHandler
import pandas as pd
import time 
import os

from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from datetime import datetime

from urllib.parse import unquote, urlparse, parse_qs


def print_message(text, color, bold=False):
    color_code = ''
    if color == 'danger':
        color_code = "\033[91m"
    elif color == 'success':
        color_code = "\033[92m" 
    elif color == 'info':
        color_code = "\033[94m"
    elif color == 'warning':
        color_code = "\033[93m"
    
    if bold == True:
        return print(f"{color_code}\033[1m{text}\033[0m")
    else:
        return print(f"{color_code}{text}\033[0m")


def scrollFromToptoBottom(dvr, boundary_component, byId=False, no_scroll_top=False, sleepTime = 5):
    scrolled = False
    timeout_scroll = 30
    scroll_count = 0
    is_boundary_component = False
    
    print('scrolled, is_boundary_component, scroll_count', scrolled, is_boundary_component, scroll_count, timeout_scroll)
    print_message(f'scrolling . . . {boundary_component}', 'info')

    while not scrolled and scroll_count < timeout_scroll and not is_boundary_component: 
        current_scroll_position = dvr.execute_script("return window.pageYOffset;")
        document_height = dvr.execute_script("return document.documentElement.scrollHeight;")
        print('current_scroll_position', current_scroll_position)
        print('document_height', document_height)
        try:
            boundary_element = dvr.find_element(by=By.CLASS_NAME, value=f'{boundary_component}') if not byId else dvr.find_element(by=By.ID, value=f'{boundary_component}')  
            if boundary_element:
                scrolled = True
                is_boundary_component = True
                scroll_count=0
        except NoSuchElementException:
            scrolled = False
            is_boundary_component = False
            scroll_height = 500
            dvr.execute_script(f"window.scrollBy(0, {scroll_height});")
            scroll_count += 1
            print('scroll_count', scroll_count)
            time.sleep(sleepTime)
        
    if is_boundary_component or scroll_count == timeout_scroll and not no_scroll_top:
        print('get_this_func_1')
        dvr.execute_script("window.scrollTo(0, 0);")
        scroll_count=0
        scrolled = False
        return [True]
    if is_boundary_component or scroll_count == timeout_scroll and no_scroll_top:
        print('get_this_func_2')
        scroll_count=0
        scrolled = False
        return [True]
    else:
        print('get_this_func_3')
        scroll_count=0
        scrolled = False
        return [False]
    
def findActiveButtons(array, attr):
    for item in array:
        if item is not None:
            if attr and item.get_attribute(attr) == 'true':
                return item.text
        return None

def flattenCustomerReviews(data, key1='', key2='', key3=''):
    flattened_data = []
    for item in [data]:
        for review in item[key1]:
            flattened_item = item.copy()
            flattened_item[key2] = review[key2]
            flattened_item[key3] = review[key3]
            del flattened_item[key1]
            flattened_data.append(flattened_item)
    return flattened_data


def extractHrefParameter(url = ''):
    # check if the url have redirect parameter
    if 'r=https' in url:
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        print('query_params', query_params)
        r_parameter_value = query_params.get('r', [])[0]
        decoded_r_value = unquote(r_parameter_value)
        return decoded_r_value
    else:
        return url

def getProductCardListDetail(driver):
    product_list_detail = []
    wait = WebDriverWait(driver, 120)
    
    all_item_each_page = driver.find_elements(By.XPATH, '//div[@class="Ms6aG"]')
    total_item_per_page = len(all_item_each_page)
    for item_index in range(int(total_item_per_page)):
        list_item_each_page = driver.find_elements(By.XPATH, '//div[@class="Ms6aG"]')
        item = list_item_each_page[item_index]
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'a')))
        sold_quantity = item.find_element(By.XPATH, '//span[@class="_1cEkb"]')
        seller_location = item.find_element(By.XPATH, '//span[@class="oa6ri"]')
        anchor = item.find_element(By.TAG_NAME, 'a')
        href = anchor.get_attribute('href')
        formatted_result = {
            'url': href,
            'quantity': seller_location.text if seller_location is not None else '',
            'location': sold_quantity.text if sold_quantity is not None else ''
        }
       
        product_list_detail.append(formatted_result)
    print('product_list_detail', product_list_detail)
    return product_list_detail


def saveDataToCSV(array=[], keyword='', status='', optionalText=''):
    current_date_time = datetime.now()
    formatted_date_time = current_date_time.strftime("%Y%m%d%H%M%S")

    stored_data = []

    if len(array) > 0:
        isArrayOfObject = False
        for i in array:
            if isinstance(i, list):
                stored_data.extend(i)
            elif isinstance(i, dict):
                isArrayOfObject = True

        if isArrayOfObject:
            stored_data = array

    if len(stored_data) > 0:
        df = pd.DataFrame(stored_data)
        df.index + 1
        df.index.rename('number', inplace=True)
        

        store_folder = 'csv_stores'
        os.makedirs(store_folder, exist_ok=True)

        success_folder = os.path.join(store_folder, 'success')
        each_product_stored_folder = os.path.join(store_folder, 'each_product_stored')
        error_folder = os.path.join(store_folder, 'error')

        os.makedirs(success_folder, exist_ok=True)
        os.makedirs(each_product_stored_folder, exist_ok=True)
        os.makedirs(error_folder, 'error')

        file_path = ''

        if status == 'success':
            file_path = os.path.join(success_folder, f'product_{keyword}_{optionalText}{formatted_date_time}.csv')
        if status == 'failed':
            file_path = os.path.join(error_folder, f'product_{keyword}_{optionalText}{formatted_date_time}.csv')
        if status == 'success_each_time':
            file_path = os.path.join(each_product_stored_folder, f'product_{keyword}_{optionalText}{formatted_date_time}.csv')
        
        df.to_csv(file_path)


def storingLoggingAs(status='', text='', additional_text=''):
    level_logging = {
        'info': logging.INFO,
        'error': logging.ERROR, 
        'warning': logging.WARNING
    }

    logs_folder = 'logs'
    os.makedirs(logs_folder, exist_ok=True)
    
    log_file_path = os.path.join(logs_folder, f'scrapper.log')
    
    handler = TimedRotatingFileHandler(log_file_path, when='H', interval=3, backupCount=24)
    handler.setLevel(level_logging[status])
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)
    logging.log(level_logging[status], f'{additional_text}{text}')



        
    #  # logging.basicConfig(filename=log_file_path, level=level_logging[status], format='%(asctime)s - %(levelname)s - %(message)s')
    # console_handler = logging.StreamHandler()
    # console_handler.setFormatter(formatter)
    # l  logging.getLogger().addHandler(handler)