import time
from bs4 import BeautifulSoup
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.by import By
from utils.helpers import playSoundWithStatus

from utils.helpers import storingLoggingAs, scrollFromToptoBottom

def getReviewDetail(driver):
    storingLoggingAs('info', f'processing review section . . . start in 30 seconds .')
    print('processing review section . . . start in 30 seconds .')

    time.sleep(30)
    detail_content = driver.page_source
    detail_soup = BeautifulSoup(detail_content, 'html.parser')
    has_empty_reviews = detail_soup.find('p', class_='empty-text')
    current_rows_of_reviewers_container = detail_soup.find('div', class_='mod-reviews')

    storingLoggingAs('info', f'has empty reviewers: {has_empty_reviews} ')
    if has_empty_reviews is None and current_rows_of_reviewers_container:
        current_rows_of_reviewers = current_rows_of_reviewers_container.find_all('div', class_='item')
        total_rows_per_page = len(current_rows_of_reviewers)

        MAX_BUTTON_PER_NAV = 7

        if len(current_rows_of_reviewers) > 0:
            review_list = []
            navigation_controller = detail_soup.find('div', class_='next-pagination-pages') if detail_soup.find('div', class_='next-pagination-pages') else None
            print('navigation_controller', navigation_controller)

            if navigation_controller is not None:
                # has pagination
                div_button_container = driver.find_element(By.XPATH, '//div[@class="next-pagination-pages"]')
               
                time.sleep(10)
                nav_button_element = div_button_container.find_elements(By.TAG_NAME, 'button')

                print('len(nav_button_element), len test', len(nav_button_element))
                storingLoggingAs('info', f'MAX_BUTTON_PER_NAV: {MAX_BUTTON_PER_NAV} -- len NAV_BUTTON_ELEMENT {len(nav_button_element)}')
                get_last_pagination_button = nav_button_element[MAX_BUTTON_PER_NAV - 2].text if len(nav_button_element) == MAX_BUTTON_PER_NAV  else nav_button_element[len(nav_button_element) - 2].text
                print('get_last_pagination_button', get_last_pagination_button)
                storingLoggingAs('info', f'total pagination: {int(get_last_pagination_button) if get_last_pagination_button else 0}')
            
                for i in range(int(get_last_pagination_button)):
                    print('processing on page', i)
                    storingLoggingAs('info', f'processing of {i} pagination with total rows per page: {total_rows_per_page}')
                    with_pagination_review_count = 0
                    with_pagination_review_count_per_page = 0
                  
                    for review_index in range(total_rows_per_page):
                        storingLoggingAs('info', f'review_index with pagination {review_index} of {total_rows_per_page}')
                     
                        customer_name_container = current_rows_of_reviewers[review_index].find('div', class_="middle")
                        cutomer_rating_container = current_rows_of_reviewers[review_index].find('div', class_="container-star starCtn left")
                        customer_review_container = current_rows_of_reviewers[review_index].find('div', class_="item-content")
                        time.sleep(2)
                       
                        customer_rating_images = cutomer_rating_container.find_all('img')
                        
                        customer_rating_source = [rating_image.attrs['src'] for rating_image in customer_rating_images]
                        customer_rating = [rate for rate in customer_rating_source if 'TB19ZvEgfDH8KJjy1XcXXcpdXXa' in rate]
                        
                        customer_name = customer_name_container.find('span').text
                      
                        customer_review = customer_review_container.find('div', class_='content').text if customer_review_container is not None else ''
                       
                        customer_sku = customer_review_container.find('div', class_="skuInfo").text if customer_review_container.find('div', class_="skuInfo") is not None else ''

                        customer_review_item = {
                            'customer_name': customer_name,
                            'customer_review': customer_review,
                            'customer_sku': customer_sku,
                            'customer_rating': len(customer_rating)
                        }

                        review_list.append(customer_review_item)
                        with_pagination_review_count += 1
                        with_pagination_review_count_per_page += 1
                    
                    storingLoggingAs('info', f' review length :{len(review_list)}')
                    storingLoggingAs('info', f'total_rows_per_page {total_rows_per_page}, with_pagination_review_count_per_page: {with_pagination_review_count_per_page} with index loop {i} ')
                    print('total_rows_per_page', total_rows_per_page, with_pagination_review_count_per_page)
                    
                    if with_pagination_review_count_per_page == total_rows_per_page:
                        print('processing pagination')
                        storingLoggingAs('info', 'processing reviews with pagination...')
                        
                        time.sleep(2)
                                  
                        next_element = driver.find_element(By.CSS_SELECTOR, '#module_product_review > div > div > div:nth-child(3) > div.next-pagination.next-pagination-normal.next-pagination-arrow-only.next-pagination-medium.medium.review-pagination > div > button.next-btn.next-btn-normal.next-btn-medium.next-pagination-item.next')
                        next_element_is_disabled = next_element.get_attribute('disabled')

                        if next_element_is_disabled:
                            storingLoggingAs('info', f'next_element_is_disabled {next_element_is_disabled} on page {i} with total {get_last_pagination_button}')
                            return review_list
                        
                        if not next_element_is_disabled or next_element_is_disabled is None:
                            try:
                                next_element.click()
                                print('clicked and scrolling in 5 seconds for 4 times')
                                scrollFromToptoBottom(driver, '', False, False, 5, 4)
                                storingLoggingAs('info','next button clicked.')

                                # Fetch the new set of current_rows_of_reviewers
                                next_element = driver.find_element(By.CSS_SELECTOR, '#module_product_review > div > div > div:nth-child(3) > div.next-pagination.next-pagination-normal.next-pagination-arrow-only.next-pagination-medium.medium.review-pagination > div > button.next-btn.next-btn-normal.next-btn-medium.next-pagination-item.next')
                                next_element_is_disabled = next_element.get_attribute('disabled')
                                
                                time.sleep(5)

                                # reset the value
                                with_pagination_review_count_per_page = 0

                                detail_content = driver.page_source
                                detail_soup_second = BeautifulSoup(detail_content, 'html.parser')

                                current_rows_of_reviewers_container_second = detail_soup_second.find('div', class_='mod-reviews')
                                current_rows_of_reviewers = current_rows_of_reviewers_container_second.find_all('div', class_='item')
                                total_rows_per_page = len(current_rows_of_reviewers)
                                time.sleep(5)
                                storingLoggingAs('info','resetting value after clicked.')
                            except ElementClickInterceptedException:
                                captcha = driver.find_element(By.XPATH, '//div[id="baxia-punish"]')
                                playSoundWithStatus('error', 3)
                                storingLoggingAs('warning',f'got captcha {captcha}')
                                if captcha:
                                    print('theres captcha, please interact with the captcha')
                                    storingLoggingAs('warning', 'captcha alert please interact with captcha. sleep in 20 seconds...')
                                    time.sleep(20)
                                    with_pagination_review_count_per_page = 0

                                    detail_content = driver.page_source
                                    detail_soup_second = BeautifulSoup(detail_content, 'html.parser')

                                    current_rows_of_reviewers_container_second = detail_soup_second.find('div', class_='mod-reviews')
                                    current_rows_of_reviewers = current_rows_of_reviewers_container_second.find_all('div', class_='item')
                                    total_rows_per_page = len(current_rows_of_reviewers)
                            except Exception as e:
                                playSoundWithStatus('error')
                                print('Exception_When_clicked', e)
                                storingLoggingAs('error', f'error exception when clicked {e}')
                                
                return review_list
            else:
                # without pagination 
        
                detail_content = driver.page_source
                detail_soup = BeautifulSoup(detail_content, 'html.parser')
                current_rows_of_reviewers_container = detail_soup.find('div', class_='mod-reviews')
                current_rows_of_reviewers = current_rows_of_reviewers_container.find_all('div', class_="item")
                total_rows = len(current_rows_of_reviewers)
                print('total_rows', total_rows)
                
                no_pagination_review_count = 0
                no_pagination_review_count_per_page = 0

                for review_index in range(total_rows):
                    customer_name_container = current_rows_of_reviewers[review_index].find('div', class_="middle")
                    cutomer_rating_container = current_rows_of_reviewers[review_index].find('div', class_="container-star starCtn left")
                    customer_review_container = current_rows_of_reviewers[review_index].find('div', class_="item-content")
                        
                    customer_rating_images = cutomer_rating_container.find_all('img')
                    
                    customer_rating_source = [rating_image.attrs['src'] for rating_image in customer_rating_images]
                    customer_rating = [rate for rate in customer_rating_source if 'TB19ZvEgfDH8KJjy1XcXXcpdXXa' in rate]
                    
                    customer_name = customer_name_container.find('span').text
                    
                    customer_review = customer_review_container.find('div', class_='content').text if customer_review_container is not None else ''
                    
                    customer_sku = customer_review_container.find('div', class_="skuInfo").text if customer_review_container.find('div', class_="skuInfo") is not None else ''
                    
                    customer_review_item = {
                        'customer_name': customer_name,
                        'customer_review': customer_review,
                        'customer_sku': customer_sku,
                        'customer_rating': len(customer_rating)
                    }

                    review_list.append(customer_review_item)

                    no_pagination_review_count += 1
                    no_pagination_review_count_per_page += 1
                    storingLoggingAs('info', f'storing without pagination succeed')
                return review_list
    else:
        # empty comments
        storingLoggingAs('info', f'empty reviewers')
        print('get_empty_comments')
        return []