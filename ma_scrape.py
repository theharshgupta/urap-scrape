from scrape import get_zipcodes, ma_download_dir, driver, NoSuchElementException
from datetime import datetime
import time
import os
from email_service import send_email

zipcodes_ma = get_zipcodes('MA')
zipcodes_ma = list(map(lambda x: '0' + str(x), zipcodes_ma))
print(zipcodes_ma)
url_ma = 'http://www.energyswitchma.gov/#/'


def new_main_scrape(zipcode):
    url_ma_recur = f'http://www.energyswitchma.gov/#/compare/2/2/{zipcode}/'
    driver.get(url_ma_recur)
    time.sleep(2)
    download_to_csv_button = driver.find_element_by_xpath(
        '/html/body/div[2]/ui-view/product-compare/div[2]/div/div[4]/button')
    download_to_csv_button.click()
    time.sleep(2)
    os.rename(
        ma_download_dir + f'EnergySwitchMass_{datetime.today().month}{datetime.today().day}{datetime.today().year}.csv',
        ma_download_dir + f'EnergySwitchMass_{zipcode}.csv')


def main_scrape(zipcode):
    driver.get(url_ma)

    driver.find_element_by_xpath('/html/body/div[2]/ui-view/home/div[1]/div[1]/div/div[2]/div/fieldset/form/div['
                                 '1]/div/div[2]/label/input').click()
    zipcode_input = driver.find_element_by_xpath(
        '/html/body/div[2]/ui-view/home/div[1]/div[1]/div/div[2]/div/fieldset/form/div['
        '2]/div/input')
    zipcode_input.clear()
    zipcode_input.send_keys(zipcode)
    driver.find_element_by_xpath('/html/body/div[2]/ui-view/home/div[1]/div[1]/div/div['
                                 '2]/div/fieldset/form/div[2]/div/button').click()

    time.sleep(1)
    try:
        dropdown = driver.find_element_by_xpath('//*[@id="distributionCompanyId"]')
        for dropdown_option in dropdown.find_elements_by_tag_name('option'):
            if 'Select' not in dropdown_option.get_attribute('label'):
                driver.get(url_ma)

                driver.find_element_by_xpath(
                    '/html/body/div[2]/ui-view/home/div[1]/div[1]/div/div[2]/div/fieldset/form/div['
                    '1]/div/div[2]/label/input').click()
                zipcode_input = driver.find_element_by_xpath(
                    '/html/body/div[2]/ui-view/home/div[1]/div[1]/div/div[2]/div/fieldset/form/div['
                    '2]/div/input')
                zipcode_input.clear()
                zipcode_input.send_keys(zipcode)
                driver.find_element_by_xpath('/html/body/div[2]/ui-view/home/div[1]/div[1]/div/div['
                                             '2]/div/fieldset/form/div[2]/div/button').click()

                dropdown_option.click()
                driver.find_element_by_xpath('/html/body/div[2]/ui-view/home/div[1]/div[1]/div/div['
                                             '2]/div/fieldset/form/div[4]/div/button').click()
                print(f"Downloaded for zipcode {zipcode}")
                time.sleep(0.5)
    except Exception as e:
        print("Error during execution and scrape fro MA")
        error_message = f"Error occurred while running the scrape for MA: \n\n {e}"
        send_email(body=error_message)
        pass

    try:
        municipal_ex = driver.find_element_by_xpath(
            '/html/body/div[2]/ui-view/home/div[1]/div[1]/div/div[2]/div/fieldset/form/div[3]/label')
        return 'Municipal Data not Available'
    except NoSuchElementException:
        pass


if __name__ == '__main__':
    for zipcode in zipcodes_ma:
        new_main_scrape(zipcode=zipcode)
