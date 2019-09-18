from selenium import webdriver
import pickle
from selenium.common.exceptions import NoSuchElementException
import re
import pandas as pd
import time

driver = webdriver.Chrome('/Users/harsh/chromedriver')


def sleep_one():
    time.sleep(1)


def scrape_website(source_url):
    """
    This is the main function, head for the scraping module that we will write for the New York
    website scrape
    :return:
    """
    # Below part accepts the agreement popup using just the clicks
    driver.get(source_url)
    time.sleep(3)
    driver.find_element_by_xpath('//*[@id="acceptOverlay"]').click()
    sleep_one()
    driver.find_element_by_xpath('//*[@id="scrollDown"]').click()
    sleep_one()
    driver.find_element_by_xpath('//*[@id="acceptOverlay"]').click()

    # Now we click the view electric popup, fuck these popups I swear
    sleep_one()
    driver.find_element_by_xpath(
        '/html/body/app-root/offer-search-component/div[2]/offer-summary-popup/div/div/div[2]/div[1]/button').click()

    # Main table data scrape now
    full_data = []
    for x in range(2, 150):
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

            print([company_name, offer_detail, rate_detail, offer_type, green_offer_details, history_pricing])
            full_data.append([company_name, offer_detail, rate_detail, offer_type, green_offer_details, history_pricing])



        except NoSuchElementException:
            break
    df = pd.DataFrame.from_records(full_data)
    df['columns'] = ['company_name', 'offer_details', 'rate', 'green', 'historic_pricing']
    df.to_csv('data.csv', index=False)

source_url = "http://documents.dps.ny.gov/PTC/zipcode/10001"
scrape_website(source_url=source_url)

# /html/body/app-root/offer-search-component/div[2]/div[4]/main/div/div/div[4]
