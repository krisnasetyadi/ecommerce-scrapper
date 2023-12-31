# import libraries
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
import time

# import custom helper functions
from utils.helpers import print_message, flattenCustomerReviews, scrollFromToptoBottomWithBoundary, storingLoggingAs
from main_functions.product_details.get_review_detail import getReviewDetail
from main_functions.product_details.get_seller_detail import getSellerDetail

def getProductDetail(driver, product_card_item):
    time.sleep(20)

    detail_content = driver.page_source
    detail_soup = BeautifulSoup(detail_content, 'html.parser')
    PRODUCT_DETAIL = {}

    product_name = detail_soup.find('h1', class_='pdp-mod-product-badge-title').text
    product_category = detail_soup.find('ul', id='J_breadcrumb')
    product_category_list = product_category.find_all('a', class_='breadcrumb_item_anchor')
    product_category_list_text = [product_category.text for product_category in product_category_list]

    if len(product_category_list_text) > 2:
        product_category_list_text.pop()

    product_category_name = " - ".join(product_category_list_text)
    product_price = detail_soup.find('span', class_='pdp-price pdp-price_type_normal pdp-price_color_orange pdp-price_size_xl').text
    product_original_price = detail_soup.find('span', class_='pdp-price pdp-price_type_deleted pdp-price_color_lightgray pdp-price_size_xs').text if detail_soup.find('span', class_='pdp-price pdp-price_type_deleted pdp-price_color_lightgray pdp-price_size_xs') is not None else ''
    
    product_detail = {
        'product_name': product_name,
        'product_category_name': product_category_name,
        'product_original_price': product_original_price if product_original_price else '',
        'product_price': product_price,
        'product_sold_quantity': product_card_item['quantity'] if product_card_item['quantity'] else ''
    }

    # UPDATE-PRODUCT-SECTION #
    PRODUCT_DETAIL.update(product_detail)
    storingLoggingAs('info', 'product detail collected')
    
    #__SELLER SECTION
    
    scroll_height = 800
    driver.execute_script(f"window.scrollBy(0, {scroll_height});")
    print('scrolled to seller section. on progress in 10 seconds . . .')
    time.sleep(10)
    
    SELLER_DETAIL = getSellerDetail(driver, product_card_item)
    
    # UPDATE-SELLER-SECTION #
    PRODUCT_DETAIL.update(SELLER_DETAIL)

    storingLoggingAs('info', 'seller detail collected')

    #__CUSTOMER REVIEW SECTION
    scroll_height2 = 1000
    driver.execute_script(f"window.scrollBy(0, {scroll_height2});")
    time.sleep(10)
    [scrolled] = scrollFromToptoBottomWithBoundary(driver, 'next-pagination-pages', False, True, 10)
    storingLoggingAs('info', f'scrolled to footer done (before get review section) {scrolled}')

    REVIEW_DETAIL = getReviewDetail(driver)

    # UPDATE-REVIEW_DETAIL-SECTION #
    storingLoggingAs('info', f'review detail collected')

    PRODUCT_DETAIL_RESULT = {}
    if REVIEW_DETAIL is not None and len(REVIEW_DETAIL) > 0:
        PRODUCT_DETAIL['customer_reviews'] = REVIEW_DETAIL
        PRODUCT_DETAIL_RESULT['result'] = flattenCustomerReviews(PRODUCT_DETAIL, 'customer_reviews', 'customer_name', 'customer_review', 'customer_sku', 'customer_rating')
    else:
        PRODUCT_DETAIL.update({'customer_name': '', 'customer_review': '', 'customer_sku': '', 'customer_rating': ''})

    return PRODUCT_DETAIL_RESULT['result'] if PRODUCT_DETAIL_RESULT else [PRODUCT_DETAIL]