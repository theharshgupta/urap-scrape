from selenium import webdriver
import pickle

driver = webdriver.Chrome('C:/chromedriver.exe')


def scrape_website(source_url):
    """
    This is the main function, head for the scraping module that we will write for the New York
    website scrape
    :return:
    """
    driver.get(source_url)
    driver.implicitly_wait(3)
    popup = driver.find_element_by_xpath('/html/body/app-root/ptc-overlay/div/div')
    driver.execute_script("arguments[0].scrollIntoView();", popup)


source_url = "http://documents.dps.ny.gov/PTC/zipcode/10001"
scrape_website(source_url=source_url)
