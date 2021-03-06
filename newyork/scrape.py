from selenium import webdriver
import pickle
from selenium.common.exceptions import NoSuchElementException
import os
import re
from bs_table_extractor import Extractor
from datetime import date
import bs4 as bs
import pandas as pd
import smtplib, ssl
import time
from email_service import send_email

ma_download_dir = "/Users/harsh/Desktop/coding/urap-scrape/ma_downloads/"
# Initialising the location for the chromedriver
chrome_options = webdriver.ChromeOptions()
prefs = {"download.default_directory": ma_download_dir}
chrome_options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(executable_path='/Users/harsh/Downloads/chromedriver', chrome_options=chrome_options)

global company_name, offer_detail, rate_detail, offer_type, green_offer_details, history_pricing


def get_zipcodes(state):
    zipcodes_list_dict = zipcodes.filter_by(state=state)
    return [int(x['zip_code']) for x in zipcodes_list_dict]


def today_date():
    """
    Return the current date in the format Date (MM/DD/YY)
    :return:
    """
    return date.today().strftime("%m/%d/%y")


def sleep_one():
    """
    Calls the time.sleep function for 1 second. The program run time pauses for 1 sec
    :return: None
    """
    time.sleep(1)


def extract_table(inner_html):
    """
    This function uses the bs_table_extractor library and uses that to extract the table from the pop up.
    :param inner_html: inner HTML code for the popup
    :return: table_extracted of type list of lists
    """
    try:
        soup = bs.BeautifulSoup(inner_html, 'html.parser')
        table = soup.find('table')
        extractor = Extractor(table)
        table_extracted = extractor.parse().return_list()
        return table_extracted
    except Exception as e:
        pass


def scrape_website(source_url, zipcode):
    """
    This is the main function, head for the scraping module that we will write for the New York
    website scrape
    :return:
    """
    # Below part accepts the agreement popup using just the clicks
    global company_name, offer_detail, rate_detail, offer_type, history_pricing, green_offer_details
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
            offer_id = element.get_attribute('id')

            for div in element.find_elements_by_tag_name('div'):
                # print(div.get_attribute('class'))
                div_class_name = div.get_attribute('class')
                if 'company-name-col' in div_class_name:
                    company_name = div.text.strip().replace('\n', '')
                elif 'offer-detail-col' in div_class_name:
                    offer_detail = div.text
                    try:
                        min_term = re.search('Min Term:(.*)', offer_detail).group(1)
                        min_term = min_term.strip('\n')
                    except Exception as e:
                        min_term = offer_detail
                elif 'rateColumn' in div_class_name:
                    rate_detail = div.text
                    try:
                        rate_per_kwh = re.search('\\n(.*)\\n', rate_detail).group(1)
                        rate_per_kwh = float(rate_per_kwh.replace('$', '').replace('per kWh', '').strip())
                    except Exception as e:
                        rate_per_kwh = rate_detail
                    try:
                        rate_per_month = float(re.search('\\n(.*)per month', rate_detail).group(1).replace('$', '')
                                               .strip())
                        units_per_month = rate_per_month / rate_per_kwh
                        units_per_month = round(units_per_month, 2)
                    except Exception as num_months_extraction_err:
                        units_per_month = 700

                elif 'offer-type-col' in div_class_name:
                    offer_type = div.text
                elif 'green-offer-col' in div_class_name:
                    green_offer_details = div.text
                elif 'historic-pricing' in div_class_name:
                    history_pricing = div.text

            print(offer_id)
            if offer_id != "":

                view_details_element = driver.find_element_by_xpath(f'//*[@id="{offer_id}"]/div[4]/span[1]/a')
                view_details_element.click()
                # sleeping for 2 seconds to make sure the table opens
                time.sleep(0.7)
                # getting the element of the popup to be sent to the extract_table function
                popup = driver.find_element_by_xpath('//*[@id="detailContent"]')
                # table_data is a list of list from the extracted table from the popup
                table_data = extract_table(inner_html=popup.get_attribute('innerHTML'))
                table_data_dict = {x[0]: str(x[1]).strip().replace('\n', '') for x in table_data}
                # Extracting cancellation fee and the EDP Compliant
                cancellation_fee = table_data_dict['Cancellation Fee']
                guaranteed_savings = table_data_dict['Guaranteed Saving']
                edp_compliant = table_data_dict['EDP Compliant']

                # closing the popup, here we use offer-table
                popup.find_element_by_class_name('close-button').click()

                data_row = [company_name, min_term, rate_per_kwh, units_per_month, guaranteed_savings, offer_type,
                            green_offer_details, history_pricing, today_date(), source_url, "New York", zipcode,
                            "Default Fixed Only NO", cancellation_fee, edp_compliant]
                if rate_detail is not '':
                    print(data_row)
                    full_data.append(data_row)
        # This is to catch if there is no element present, so it breaks out of the loop and just exits
        except NoSuchElementException or Exception as e:
            print("ERROR\n", e)
            if '"method":"xpath","selector":"/html/body/app-root/offer-search' in str(e) and f'div[{x}]' in str(e):
                break
            pass

            # else:
            #     # send_email(body=error_message)
            #     break

    df = pd.DataFrame.from_records(full_data)
    df.to_csv('data.csv', index=False)


if __name__ == '__main__':
    for zipcode in get_zipcodes('NY')[0:100]:
        source_url = f"http://documents.dps.ny.gov/PTC/zipcode/{zipcode}"
        scrape_website(source_url=source_url, zipcode=zipcode)
