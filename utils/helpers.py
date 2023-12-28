from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import logging
import pygame
import time 
import sys
import os

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


def scrollFromToptoBottom(dvr, no_scroll_top=False, sleepTime = 5, timeout=12):
    scrolled = False
    timeout_scroll = timeout
    scroll_count = 0
    max_scrolled = False

    while not scrolled and scroll_count < timeout_scroll and not max_scrolled: 
        if timeout_scroll == scroll_count:
            max_scrolled = True
        else:
            scrolled = False
            scroll_height = 400
            dvr.execute_script(f"window.scrollBy(0, {scroll_height});")
            scroll_count += 1
            print('scroll_count', scroll_count)
            time.sleep(sleepTime)
        
    if no_scroll_top == False:
        if scroll_count == timeout_scroll or max_scrolled:
            dvr.execute_script("window.scrollTo(0, 0);")
            return [True]
        
    if no_scroll_top == True:
        if max_scrolled or scroll_count == timeout_scroll:
            return [True]
    else:
        return [False]
    

def scrollFromToptoBottomWithBoundary(dvr, boundary_component, byId=False, no_scroll_top=False, sleepTime = 5):
    scrolled = False
    timeout_scroll = 15
    scroll_count = 0
    is_boundary_component = False

    while not scrolled and scroll_count < timeout_scroll and not is_boundary_component: 
        # current_scroll_position = dvr.execute_script("return window.pageYOffset;")
        # document_height = dvr.execute_script("return document.documentElement.scrollHeight;")
        # print('current_scroll_position', current_scroll_position)
        # print('document_height', document_height)
        try:
            boundary_element = dvr.find_element(by=By.CLASS_NAME, value=f'{boundary_component}') if not byId else dvr.find_element(by=By.ID, value=f'{boundary_component}')  
            if boundary_element:
                scrolled = True
                is_boundary_component = True
        except NoSuchElementException:
            scrolled = False
            is_boundary_component = False
            scroll_height = 400
            dvr.execute_script(f"window.scrollBy(0, {scroll_height});")
            scroll_count += 1
            print('scroll__with_boundary_count', scroll_count)
            time.sleep(sleepTime)
        
    if no_scroll_top == False:
        if scroll_count == timeout_scroll or is_boundary_component:
            dvr.execute_script("window.scrollTo(0, 0);")
            return [True]
        
    if no_scroll_top == True:
        if is_boundary_component or scroll_count == timeout_scroll:
            return [True]
    else:
        return [False]
    
def findActiveButtons(array, attr):
    for item in array:
        if item is not None:
            if attr and item.get_attribute(attr) == 'true':
                return item.text
        return None

def flattenCustomerReviews(data, key1='', key2='', key3='', key4='', key5=''):
    flattened_data = []
    for item in [data]:
        for review in item[key1]:
            flattened_item = item.copy()
            flattened_item[key2] = review[key2]
            flattened_item[key3] = review[key3]
            flattened_item[key4] = review[key4]
            flattened_item[key5] = review[key5]
            del flattened_item[key1]
            flattened_data.append(flattened_item)
    return flattened_data

def getProductCardListDetail(driver):
    product_list_detail = []
    wait = WebDriverWait(driver, 120)
    item_per_page_container = driver.find_elements(By.XPATH, '//div[@class="Bm3ON"]')
    total_item_per_page = len(item_per_page_container)

    print('getProductCardListDetail first and econd', f'1 {total_item_per_page}')
    drive_page_source = driver.page_source
    content_soup = BeautifulSoup(drive_page_source, 'html.parser')
    item_per_page_soup = content_soup.find_all('div', class_='Bm3ON')
    print(f'item_per_page_soup {len(item_per_page_soup)}')
    for item_index in range(int(total_item_per_page)):
        print(f'processing card list detail. processing on current index {item_index} of {total_item_per_page}')

        item_per_page_container = driver.find_elements(By.XPATH, '//div[@class="Bm3ON"]')
        item = item_per_page_container[item_index]
        quantity_container = item_per_page_soup[item_index].find('div', class_="_6uN7R")
        sold_quantity = quantity_container.find('span', class_="_1cEkb").text if quantity_container.find('span', class_="_1cEkb") is not None else ''
        time.sleep(2)

        seller_location = content_soup.find_all('span', class_='oa6ri') 

        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'a')))
        anchor = item.find_element(By.TAG_NAME, 'a')
        href = anchor.get_attribute('href')

        formatted_result = {
            'url': href,
            'location': seller_location[item_index].text if seller_location[item_index] else '',
            'quantity': sold_quantity
        }

        product_list_detail.append(formatted_result)
    return product_list_detail


def saveDataToCSV(array=[], keyword='', status='', optionalText=''):
    current_date_time = datetime.now()
    formatted_date_time = current_date_time.strftime("%Y%m%d%H%M%S")
    # storingLoggingAs('info', f'array_before_save_to_csv {array}')
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

    current_storing_size = sys.getsizeof(stored_data)
    current_array_size = sys.getsizeof(array)
    storingLoggingAs('warning', f'size_of_array {current_array_size} -- size_of_storing {current_storing_size}')
    # storingLoggingAs('info', f'stored data {stored_data}')
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
        os.makedirs(error_folder, exist_ok=True)

        file_path = ''

        if status == 'success':
            file_path = os.path.join(success_folder, f'product_{keyword}_{optionalText}{formatted_date_time}.csv')
        if status == 'failed':
            file_path = os.path.join(error_folder, f'product_{keyword}_{optionalText}{formatted_date_time}.csv')
        if status == 'success_each_item':
            file_path = os.path.join(each_product_stored_folder, f'product_{keyword}_{optionalText}{formatted_date_time}.csv')
        
        df.to_csv(file_path)
        playSoundWithStatus('success')


def storingLoggingAs(status='', text=''):
    current_date_time = datetime.now()
    formatted_date_time = current_date_time.strftime("%Y%m%d")

    level_logging = {
        'info': logging.INFO,
        'error': logging.ERROR, 
        'warning': logging.WARNING
    }

    logs_folder = 'logs'
    os.makedirs(logs_folder, exist_ok=True)
    
    log_file_path = os.path.join(logs_folder, f'scrapper_{formatted_date_time}.log')

    logger = logging.getLogger('logger') 
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(level_logging[status])
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

    logger.log(level_logging[status], f'{text}')
    
    
def playSoundWithStatus(status='error', times=1):
    pygame.mixer.init()
   
    sound_by_status = pygame.mixer.Sound(f'./sound_asset/{"blinking_bell_loop" if status == "error" else "bells_deep"}.wav')
   
    for i in range(times):
        sound_by_status.play()
        print(f'sound played in {i} time')
        pygame.time.wait(int(sound_by_status.get_length() * 1000))
