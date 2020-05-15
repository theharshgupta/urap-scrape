from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from difflib import SequenceMatcher
import email_error
import time
import bs4 as bs


def scrape(supplier):
    oldHTML = open("./data/" + supplier + ".html").read()
    driver = webdriver.Chrome()
    #driver = webdriver.Chrome(r'C:/Program Files/Chromedriver/chromedriver.exe') 
    driver.get("https://www.energizect.com/compare-energy-suppliers")  # get the page

    if (supplier == "ui"):
        ui_button = driver.find_element_by_id("radioTwo")
        ui_button.click()
    # Click the button
    compare_now_button = driver.find_element_by_class_name("supplier_form_submit")
    compare_now_button.click()

    # Wait *up to* 20 seconds for the popup to show up 
    try:
        WebDriverWait(driver,20).until(EC.visibility_of_element_located((By.CLASS_NAME, "close_anchor")))
    except: 
        email_error.send_email("selenium timed out")

    #click the x for a disclaimer
    close_button = driver.find_element_by_class_name("clostPopup")
    close_button.click()

    # Get the html
    html = driver.page_source

    #writing to a file
    soup = bs.BeautifulSoup(html, 'html.parser')
    html = soup.prettify() 
    with open("./data/" + supplier + ".html","w") as out:
        for i in range(0, len(html)):
            try:
                out.write(html[i])
            except Exception:
                1+1
    newHTML = open("./data/" + supplier + ".html").read()

    #calculates percentage difference between this and the last relevant HTML file
    matcher = SequenceMatcher(None, oldHTML, newHTML).quick_ratio()
    if matcher < 0.5:
        email_error.send_email("difference between HTML files is: ", matcher)
    print("percent match:", matcher)