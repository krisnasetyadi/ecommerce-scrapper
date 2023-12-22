import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

from utils.helpers import storingLoggingAs

def getReviewDetail(driver):
    print('processing review section . . .')
    
    time.sleep(60)
    detail_content = driver.page_source
    detail_soup = BeautifulSoup(detail_content, 'html.parser')
    has_empty_reviews = detail_soup.find('p', class_='empty-text')
    storingLoggingAs('info', f'has empty reviewers: {has_empty_reviews}')
    if has_empty_reviews is not None:
        current_rows_of_reviewers_container = detail_soup.find_all('div', class_='mod-reviews')
        current_rows_of_reviewers = current_rows_of_reviewers_container.find_all('div', class_='item')
        total_rows_per_page = len(current_rows_of_reviewers)
        print('total_rows_per_page', total_rows_per_page)
        print('current_rows_of_reviewers', current_rows_of_reviewers)

        MAX_BUTTON_PER_NAV = 7

        # there's some reviews next-btn next-btn-normal next-btn-medium next-pagination-item next
        if len(current_rows_of_reviewers) > 0:
            review_list = []
            navigation_controller = detail_soup.find('div', class_='next-pagination-pages') if detail_soup.find('nav', class_='next-pagination-pages') is not None else ''
            print('navigation_controller', navigation_controller)

            if navigation_controller is not None:
                # has pagination
                div_button_container = driver.find_element(By.XPATH, '//div[@class="next-pagination-pages"]')
                nav_button_element = div_button_container.find_elements(By.XPATH, '//button[@class="next-btn next-btn-normal next-btn-medium next-pagination-item"]')
                last_pagination_button = nav_button_element[MAX_BUTTON_PER_NAV - 1].text if len(nav_button_element) == MAX_BUTTON_PER_NAV  else nav_button_element[len(nav_button_element) - 1].text

                storingLoggingAs('info', f'total pagination: {int(last_pagination_button)}')
                for i in range(int(last_pagination_button)):
                    storingLoggingAs('info', f'processing of {i} pagination with total rows per page: {total_rows_per_page}')
                    with_pagination_review_count = 0
                    with_pagination_review_count_per_page = 0

                    div_button_container = driver.find_element(By.XPATH, '//div[@class="next-pagination-pages"]')
                    nav_button_element = div_button_container.find_elements(By.XPATH, '//button[@class="next-btn next-btn-normal next-btn-medium next-pagination-item"]')

                    for review_index in range(total_rows_per_page):
                        customer_name_container = current_rows_of_reviewers[review_index].find('div', class_='middle')
                        cutomer_rating_container = current_rows_of_reviewers[review_index].find('div', class_='container-star starCtn left')
                        customer_review_container = current_rows_of_reviewers[review_index].find('div', class_='item-content')
                        
                        customer_rating_images = cutomer_rating_container.find_all('img')
                        customer_rating_source = [rating_image.attrs['src'] for rating_image in customer_rating_images]
                        customer_rating = [rate for rate in customer_rating_source if 'TB19ZvEgfDH8KJjy1XcXXcpdXXa' in rate]
                        
                        customer_name = customer_name_container.find('span').text
                        
                        customer_review = customer_review_container.find('div', class_='content').text if customer_review_container is not None else ''
                        customer_sku = customer_review_container.find('div', class_='skuInfo').text if customer_review_container is not None else ''

                        customer_review_item = {
                            'customer_name': customer_name,
                            'customer_review': customer_review,
                            'customer_rating': customer_rating,
                            'customer_sku': customer_sku
                        }

                        review_list.append(customer_review_item)
                        with_pagination_review_count += 1
                        with_pagination_review_count_per_page += 1

                    if with_pagination_review_count_per_page == total_rows_per_page:

                        storingLoggingAs('info', 'processing reviews with pagination...')
                        # why CLASS_NAME "next-pagination-pages" declare twice ? to always refresh /fetch the element
                        nav_button_container_second = driver.find_element(By.XPATH, '//div[@class="next-pagination-pages"]')
                        time.sleep(2)
                        next_element = nav_button_container_second.find_element(By.XPATH, '//button[@class="next-btn next-btn-normal next-btn-medium next-pagination-item next"]')
                        next_element_is_disabled = next_element.get_attribute('disabled')

                        if next_element_is_disabled:
                            return review_list
                        
                        if not next_element_is_disabled or next_element_is_disabled is None:
                            next_element.click()
                            storingLoggingAs('info','next button clicked.')
                            next_element = nav_button_container_second.find_element(By.XPATH, '//button[@class="next-btn next-btn-normal next-btn-medium next-pagination-item next"]')
                            next_element_is_disabled = next_element.get_attribute('disabled')

                            # reset the value and click
                            with_pagination_review_count_per_page = 0

                            time.sleep(5)

                            # Fetch the new set of current_rows_of_reviewers
                            next_element = nav_button_container_second.find_element(By.XPATH, '//button[@class="next-btn next-btn-normal next-btn-medium next-pagination-item next"]')
                            detail_content = driver.page_source
                            detail_soup_second = BeautifulSoup(detail_content, 'html.parser')

                            current_rows_of_reviewers_container = detail_soup_second.find_all('div', class_='mod-reviews')
                            current_rows_of_reviewers = current_rows_of_reviewers_container.find_all('div', class_='item')
                            total_rows_per_page = len(current_rows_of_reviewers)
                            storingLoggingAs('info','resetting value after clicked.')
                return review_list
            else:
                # without pagination 
        
                detail_content = driver.page_source
                detail_soup_second = BeautifulSoup(detail_content, 'html.parser')
                current_rows_of_reviewers_container = detail_soup_second.find_all('div', class_='mod-reviews')
                current_rows_of_reviewers = current_rows_of_reviewers_container.find_all('div', class_='item')
                no_pagination_review_count = 0
                no_pagination_review_count_per_page = 0

                for review_index in range(current_rows_of_reviewers):
                    customer_name_container = current_rows_of_reviewers[review_index].find('div', class_='middle')
                    cutomer_rating_container = current_rows_of_reviewers[review_index].find('div', class_='container-star starCtn left')
                    customer_review_container = current_rows_of_reviewers[review_index].find('div', class_='item-content')
                    
                    customer_rating_images = cutomer_rating_container.find_all('img')
                    customer_rating_source = [rating_image.attrs['src'] for rating_image in customer_rating_images]
                    customer_rating = [rate for rate in customer_rating_source if 'TB19ZvEgfDH8KJjy1XcXXcpdXXa' in rate]
                    
                    customer_name = customer_name_container.find('span').text
                    
                    customer_review = customer_review_container.find('div', class_='content').text if customer_review_container is not None else ''
                    customer_sku = customer_review_container.find('div', class_='skuInfo').text if customer_review_container is not None else ''

                    customer_review_item = {
                        'customer_name': customer_name,
                        'customer_review': customer_review,
                        'customer_rating': customer_rating,
                        'customer_sku': customer_sku
                    }

                    review_list.append(customer_review_item)

                    no_pagination_review_count += 1
                    no_pagination_review_count_per_page += 1
                    storingLoggingAs('info', f'storing without pagination succeed')
                return review_list
    else:
        # empty comments
        
        print('get_empty_comments')
        return []