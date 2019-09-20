from selenium import webdriver
import pickle
from selenium.common.exceptions import NoSuchElementException
import os
import re
from bs_table_extractor import Extractor
from datetime import date
import bs4 as bs
import pandas as pd
import time

# Initialising the location for the chromedriver
driver = webdriver.Chrome('/Users/harsh/chromedriver')


def today_date():
    """
    Return the current date in the format Date (MM/DD/YY)
    :return:
    """
    return date.today().strftime("%m/%d/%y")


def sleep_one():
    """
    Calls the time.sleep function for 1 second. The program run time pauses for 1 second
    :return: None
    """
    time.sleep(1)


def extract_table(inner_html):
    """
    This function uses the bs_table_extractor library and uses that to extract the table from the pop up.
    :param inner_html: inner HTML code for the popup
    :return: table_extracted of type list of lists
    """
    soup = bs.BeautifulSoup(inner_html, 'html.parser')
    table = soup.find('table')
    extractor = Extractor(table)
    table_extracted = extractor.parse().return_list()
    return table_extracted


def scrape_website(source_url, zipcode):
    """
    This is the main function, head for the scraping module that we will write for the New York
    website scrape
    :return:
    """
    # Below part accepts the agreement popup using just the clicks
    driver.get(source_url)
    try:
        time.sleep(1)
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
            offer_id = element.get_attribute('id')

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

            # clicking the view details button
            view_details_element = driver.find_element_by_xpath(f' //*[@id="{offer_id}"]/div[4]/span[1]/a')
            view_details_element.click()
            # sleeping for 2 seconds to make sure the table opens
            time.sleep(1)
            # getting the element of the popup to be sent to the extract_table function
            popup = driver.find_element_by_xpath('//*[@id="detailContent"]')
            # table_data is a list of list from the extracted table from the popup
            table_data = extract_table(inner_html=popup.get_attribute('innerHTML'))
            print(pd.DataFrame.from_records(table_data).to_string())
            # closing the popup, here we use offer-tabloe
            popup.find_element_by_class_name('close-button').click()

            data_row = [company_name, offer_detail, rate_detail, offer_type, green_offer_details, history_pricing,
                        today_date(), source_url, "New York", zipcode, "Default Fixed Only NO", ]
            if rate_detail is not '':
                print(data_row)
                full_data.append(data_row)

        except NoSuchElementException or Exception as e:
            print("ERROR\n", e)
            break
    df = pd.DataFrame.from_records(full_data)
    df.to_csv('data.csv', index=False)
    # print(df.to_string())


for zipcode in range(10001, 10002):
    source_url = f"http://documents.dps.ny.gov/PTC/zipcode/{zipcode}"
    scrape_website(source_url=source_url, zipcode=zipcode)

# database schema for basic data download from the website

"""
Date Downloaded

State

Website/Provider
TDU Service Territory
Updated since previous pull?
Defaults to Fixed Rates Only
Default Monthly Usage for Calculating Bills and Savings
Price to Compare / Default Rate for Calculating Bills and Savings
"""
