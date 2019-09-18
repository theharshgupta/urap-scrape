from selenium import webdriver
import pickle
from selenium.common.exceptions import NoSuchElementException
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
    for x in range(3, 150):
        try:
            element = driver.find_element_by_xpath(f"/html/body/app-root/offer-search-component/div[2]/div[4]/main/div/div/div[{x}]")
            print(element.text)
        except NoSuchElementException:
            break



    # data_rows = driver.find_elements_by_class_name('row dataRow')
    # print("Data Rows:", data_rows)
    # for element in data_rows:
    #     print("Element:", element)


source_url = "http://documents.dps.ny.gov/PTC/zipcode/10001"
scrape_website(source_url=source_url)

# /html/body/app-root/offer-search-component/div[2]/div[4]/main/div/div/div[4]