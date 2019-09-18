from selenium import webdriver
import pickle
from selenium.common.exceptions import NoSuchElementException
import os
import re
import pandas as pd
import time

# Initialising the location for the chromedriver
driver = webdriver.Chrome('/Users/harsh/chromedriver')


def sleep_one():
    """
    Calls the time.sleep function for 1 second. The program run time pauses for 1 second
    :return:
    """
    time.sleep(1)


def scrape_website(source_url):
    """
    This is the main function, head for the scraping module that we will write for the New York
    website scrape
    :return:
    """
    # Below part accepts the agreement popup using just the clicks
    driver.get(source_url)
    try:
        time.sleep(3)
        driver.find_element_by_xpath('//*[@id="acceptOverlay"]').click()
        sleep_one()
        driver.find_element_by_xpath('//*[@id="scrollDown"]').click()
        sleep_one()
        driver.find_element_by_xpath('//*[@id="acceptOverlay"]').click()
    except NoSuchElementException:
        pass

    # Now we click the view electric popup, fuck these popups I swear
    sleep_one()
    driver.find_element_by_xpath(
        '/html/body/app-root/offer-search-component/div[2]/offer-summary-popup/div/div/div[2]/div[1]/button').click()

    # Main table data scrape now
    full_data = []
    for x in range(2, 1500):
        "Here we can put this to an arbitrary large number just for the sake of the loop"
        try:
            element_xpath = f"/html/body/app-root/offer-search-component/div[2]/div[4]/main/div/div/div[{x}]"
            element = driver.find_element_by_xpath(element_xpath)
            element_id = element
            divs = element.find_elements_by_tag_name('div')
            # print('\t', len(divs))

            for div in element.find_elements_by_tag_name('div'):
                # print(div.get_attribute('class'))
                div_class_name = div.get_attribute('class')
                if 'company-name-col' in div_class_name:
                    company_name = div.text.strip().replace('\n', '')
                elif 'offer-detail-col' in div_class_name:
                    offer_detail = div.text
                elif 'rateColumn' in div_class_name:
                    rate_detail = div.text
                elif 'offer-type-col' in div_class_name:
                    offer_type = div.text
                elif 'green-offer-col' in div_class_name:
                    green_offer_details = div.text
                elif 'historic-pricing' in div_class_name:
                    history_pricing = div.text

            data_row = [company_name, offer_detail, rate_detail, offer_type, green_offer_details, history_pricing]
            if rate_detail is not '':
                print(data_row)
                full_data.append(data_row)

        except NoSuchElementException:
            break
    df = pd.DataFrame.from_records(full_data)
    df.to_csv('data.csv', index=False)
    print(df.to_string())


for zip_code in range(10001, 10003):
    source_url = f"http://documents.dps.ny.gov/PTC/zipcode/{zip_code}"
    scrape_website(source_url=source_url)
