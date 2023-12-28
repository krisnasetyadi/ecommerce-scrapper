from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By

from utils.helpers import scrollFromToptoBottom, saveDataToCSV, storingLoggingAs, print_message, playSoundWithStatus

from main_functions.product_details.get_main_product_detail import getProductDetail

import time

def openNewTabWindow(driver, product_card_item, listOfProduct, keyword, index_item, total_item):
    #open blank tab
    driver.execute_script("window.open('', '_blank');")
    print('processing_opening_new_tab')
    driver.switch_to.window(driver.window_handles[-1])
    storingLoggingAs('info', f'opening url: {product_card_item["url"]}')
    driver.get(product_card_item["url"])

    [scrolled] = scrollFromToptoBottom(driver, '', False, False, 10, 12)
    storingLoggingAs('info', f'scrolled finished: {scrolled}. trying to process and collect product detail')

    try:
        get_product_detail = getProductDetail(driver, product_card_item)
        listOfProduct.append(get_product_detail)
        time.sleep(30)
        saveDataToCSV(listOfProduct, keyword, 'success_each_item', 'each_product')
        storingLoggingAs('info', f'successfully saved in each products folder {index_item} of {total_item}')
       
        
    except WebDriverException as e:
          playSoundWithStatus('error', 2)
          if(len(listOfProduct) > 0):
            saveDataToCSV(listOfProduct, keyword, 'failed', 'action_failed')
            storingLoggingAs('error', f'product error gets: {e}')
            
    except Exception as e:
        playSoundWithStatus('error', 2)
        print_message(f'error_from openNewTabWindow func {e}', 'danger', False)
        if(len(listOfProduct) > 0):
            saveDataToCSV(listOfProduct, keyword, 'failed', 'action_failed')
            storingLoggingAs('error', f'product error gets: {e}')

    driver.close()

    driver.switch_to.window(driver.window_handles[0])

    print('close the tab')




def getTotalPagination(driver):
    MAX_BUTTON_PAGINATION = 8
            
    div_pagination_container = driver.find_element(By.XPATH, '//div[@class="b7FXJ"]')
    nav_product_pagination_element = div_pagination_container.find_elements(By.TAG_NAME, 'li')

    print('BUTTTON_ELEMENT', nav_product_pagination_element)
    print('len(nav_product_pagination_element), len test', len(nav_product_pagination_element))
    get_last_pagination_button = nav_product_pagination_element[MAX_BUTTON_PAGINATION - 2].text if len(nav_product_pagination_element) == MAX_BUTTON_PAGINATION  else nav_product_pagination_element[len(nav_product_pagination_element) - 2].text
    storingLoggingAs('info', f'MAX_BUTTON_PAGINATION: {MAX_BUTTON_PAGINATION} -- len NAV_PRODUCT_PAGINATION_ELEMENT {len(nav_product_pagination_element)} TOTAL_PRODUCT_PAGINATION_LIST: {get_last_pagination_button}')
    return get_last_pagination_button
