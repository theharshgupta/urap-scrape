from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
import bs4 as bs

driver = webdriver.Chrome()
driver.get("https://www.energizect.com/compare-energy-suppliers")  # get the page

# Click the button
compare_now_button = driver.find_element_by_class_name("supplier_form_submit")
compare_now_button.click()

# Wait *up to* 10 seconds to make sure the page has finished loading (check that the button no longer exists)
# WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.CLASS_NAME, "supplier_form_submit")))

#wait for the x to show up 
WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.CLASS_NAME, "close_anchor")))

#click the x for a disclaimer
close_button = driver.find_element_by_class_name("clostPopup")
close_button.click()


action = ActionChains(driver)


lists = driver.find_elements_by_class_name("compare_button1")
count = 0

for test_button1 in lists:
    action.move_to_element(test_button1).perform()
    #action.click(test_button1).perform()
    #while True:
        #try:
            #close = driver.find_element_by_class_name("ui-button-icon-primary ui-icon ui-icon-closethick")
            #close2 = driver.find_element_by_class_name("ui-button ui-widget ui-state-default ui-corner-all ui-button-icon-only ui-dialog-titlebar-close")

            #action.move_to_element(close2).perform()
            #action.click(close2).perform()
            #break
        #except Exception:
            #time.sleep(3)
            #print("wait")
    count += 1
    print(count)

# Get the html
html = driver.page_source

#writing to a file
soup = bs.BeautifulSoup(html, 'html.parser')
html = soup.prettify() 
with open("out.html","w") as out:
    for i in range(0, len(html)):
        try:
            out.write(html[i])
        except Exception:
            1+1

