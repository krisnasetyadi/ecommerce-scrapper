from selenium.common.exceptions import WebDriverException

from utils.helpers import scrollFromToptoBottom, saveDataToCSV, storingLoggingAs

from main_functions.product_details.get_main_product_detail import getProductDetail
import time

def openNewTabWindow(driver, cart_list_item, listOfProduct, keyword):
    #open blank tab
    driver.execute("window.open('', '_blank');")
    driver.switch_to_window(driver.window_handles[-1])
    storingLoggingAs('info', f'opening url: {cart_list_item["url"]}')
    driver.get(cart_list_item["url"])

    [scrolled] = scrollFromToptoBottom(driver, '', False, True, 5)
    storingLoggingAs('info', f'scrolled finished: {scrolled}. trying to process and collect product detail')

    try:
        get_product_detail = getProductDetail(driver, cart_list_item)
        listOfProduct.append(get_product_detail)
        time.sleep(30)
        saveDataToCSV(listOfProduct, keyword, 'success_each_item', 'each_product')
        storingLoggingAs('info', 'successfully saved in each products folder')
    except WebDriverException as e:
          if(len(listOfProduct) > 0):
            saveDataToCSV(listOfProduct, keyword, 'failed', 'action_failed')
            storingLoggingAs('error', f'product error gets: {e}')

    driver.close()

    driver.switch_to_window(driver.window_handle[0])