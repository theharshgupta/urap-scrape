from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
from difflib import SequenceMatcher
import email_error
import bs4 as bs

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--window-size=1440, 900")

def scrape(supplier):

    #driver = webdriver.Chrome()
    driver = webdriver.Chrome(r'/usr/lib/chromium-browser/chromedriver', options=options)

    driver.get("https://www.energizect.com/compare-energy-suppliers")  # get the page

    if (supplier == "UI"):
        ui_button = driver.find_element_by_id("radioTwo")
        ui_button.click()
    # Click the button
    compare_now_button = driver.find_element_by_class_name("supplier_form_submit")
    compare_now_button.click()
    
    # Wait *up to* 10 seconds to make sure the page has finished loading (check that the button no longer exists)
    # WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.CLASS_NAME, "supplier_form_submit")))

    #TEMPERORARY FOR THE POPUP ABOUT STANDARD PRICES
    try:
        WebDriverWait(driver,30).until(EC.visibility_of_element_located((By.CLASS_NAME, "ui-dialog-titlebar-close")))
        close_button = driver.find_element_by_class_name("ui-dialog-titlebar-close")
        close_button.click()
    except: 
        print("no seasonal popup")
    
    # Wait *up to* 20 seconds for the popup to show up 
    try:
        WebDriverWait(driver,30).until(EC.visibility_of_element_located((By.CLASS_NAME, "close_anchor")))
    except: 
        email_error.send_email("no close anchor")
    
    #click the x for a disclaimer
    close_button = driver.find_element_by_class_name("clostPopup")
    close_button.click()
    action = ActionChains(driver)
    

    lists = driver.find_elements_by_class_name("compare_button1")
    count = 0
    try:
        oldHTML = open("./data/" + supplier + "_PVD.html").read()
        flag_first = 0
    except Exception:
        1 + 1
        flag_first = 1
        print("didn't find old")
    for test_button1 in lists:
        #try:
        action.move_to_element(test_button1).perform()
        #test_button1.click()
        #except Exception:
        #    time.sleep(5)
        #    print("slept")
        count += 1
        # print(count)
    

    html = driver.page_source
    
    #writing to a file
    soup = bs.BeautifulSoup(html, 'html.parser')
    html = soup.prettify()
    error_chrs = []
    with open("./data/" + supplier + "_PVD.html","w") as out:
        for i in range(0, len(html)):
            try:
                out.write(html[i])
            except Exception:
                1+1
                error_chrs.append(html[i])
    #print("Wrote all characters to HTML file for past variable rates scrape except:")
    #print(set(error_chrs))
    
    # Calculate percentage difference between this and the last relevant HTML file
    if flag_first == 0:
        newHTML = open("./data/"  + supplier + "_PVD.html").read()
        matcher = SequenceMatcher(None, oldHTML, newHTML).quick_ratio()
        if matcher < 0.5:
            email_error.send_email("difference between HTML files is: ", matcher)
        print("percent match:", matcher)
        
    # End webdriver session
    driver.quit()