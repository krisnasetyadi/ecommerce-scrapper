from bs4 import BeautifulSoup

def getSellerDetail(driver, product_card_item):
    print('processing seller detail')
    detail_content = driver.page_source
    detail_soup = BeautifulSoup(detail_content, 'html.parser')
    seller_name_container = detail_soup.find('div', class_='seller-name__detail')
    seller_name = seller_name_container.find('a').text 

    seller_performance = detail_soup.find_all('div', class_='seller-info-value')
    seller_chat_responsiveness = seller_performance[2].text if seller_performance[2] is not None else ''
    seller_ship_responsiveness = seller_performance[1].text if seller_performance[1] is not None else ''
    seller_rating = seller_performance[0].text if seller_performance[0] is not None else ''

    seller_category_image = detail_soup.find('img', class_='pdp-mod-product-badge') if detail_soup.find('img', class_='pdp-mod-product-badge') is not None else ''
    seller_badge_category = seller_category_image.attrs['alt'] if seller_category_image  else ''

    seller_location = ''
    if product_card_item['location'] is not None or product_card_item['location'] != '':
        seller_location = product_card_item['location']
    else:
        seller_location = ''

    seler_section = {
        'seller_name' : seller_name,
        'performance_seller_responsiveness': seller_chat_responsiveness,
        'performance_seller_seller_rating': seller_rating,
        'performance_seller_ship_on_time': seller_ship_responsiveness,
        'seller_badge_category': seller_badge_category,
        'seller_location': seller_location,
    }
    return seler_section
