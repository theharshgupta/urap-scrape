from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import bs4 as bs
from bs4 import BeautifulSoup


driver = webdriver.Chrome()
driver.get("https://www.energizect.com/compare-energy-suppliers")  # get the page

# Click the button
compare_now_button = driver.find_element_by_class_name("supplier_form_submit")
compare_now_button.click()

# Wait *up to* 10 seconds to make sure the page has finished loading (check that the button no longer exists)
WebDriverWait(driver,10).until(EC.invisibility_of_element_located((By.CLASS_NAME, "supplier_form_submit")))

#wait for the x to show up 
WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.CLASS_NAME, "close_anchor")))

#click the x for a disclaimer
close_button = driver.find_element_by_class_name("clostPopup")
close_button.click()

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

print(html)

with open('out.html') as ex:
    soup2 = BeautifulSoup(ex, 'html.parser')

table = soup2.find_all('table', class_ = "nice_table responsive highlight_table display nowrap")
table = table[0]
for row in table.find_all('tr'):
    for cell in row.find_all('td'):
        print(cell.attrs)
