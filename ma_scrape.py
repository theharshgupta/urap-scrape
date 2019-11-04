from scrape import get_zipcodes, ma_download_dir, driver, NoSuchElementException
from datetime import datetime
import time
import os
import pandas as pd
from email_service import send_email

zipcodes_ma = get_zipcodes('MA')
zipcodes_ma = list(map(lambda x: '0' + str(x), zipcodes_ma))
print(zipcodes_ma)
url_ma = 'http://www.energyswitchma.gov/#/'


def format_csv():
    global service_territory, customer_class, product_filter, contract_term, min_monthly_cost, max_monthly_cost, min_contract_term, max_contract_term, product_sorting, supplier_list
    import csv
    for file in os.listdir('ma_downloads'):
        with open('ma_downloads/' + file) as csv_file:
            reader = csv.reader(csv_file)
            csv_list = list(reader)
        if csv_list:
            for index, line in enumerate(csv_list):
                if len(line) > 0:
                    if 'Service Territory' in line[0]:
                        service_territory = line[-1]
                    elif 'Customer Class' in line[0]:
                        customer_class = line[-1]
                    elif 'Product Filter' in line[0]:
                        product_filter = line[-1]
                    elif 'Contract Term' in line[0]:
                        contract_term = line[-1]
                    elif 'Minimum Monthly cost' in line[0]:
                        min_monthly_cost = line[-1]
                    elif 'Maximum Monthly cost' in line[0]:
                        max_monthly_cost = line[-1]
                    elif 'Minimum Contract Term' in line[0]:
                        min_contract_term = line[-1]
                    elif 'Maximum Contract Term' in line[0]:
                        max_contract_term = line[-1]
                    elif 'Product Sorting' in line[0]:
                        product_sorting = line[-1]
                    if len(line) > 0:
                        if line[0] == 'Supplier Name':
                            supplier_list = csv_list[index:]
                            break
            print([service_territory, customer_class, product_filter, contract_term, min_monthly_cost, max_monthly_cost,
                  product_sorting])
            df = pd.DataFrame.from_records(supplier_list)
            df.columns = list(df.values.tolist())[0]
            df = df[1:]
            df.to_csv(f'ma_csvs/{file}', index=False)

def new_main_scrape(zipcode):
    url_ma_recur = f'http://www.energyswitchma.gov/#/compare/4/1/{zipcode}/'
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
        # send_email(body=error_message)
        pass

    try:
        municipal_ex = driver.find_element_by_xpath(
            '/html/body/div[2]/ui-view/home/div[1]/div[1]/div/div[2]/div/fieldset/form/div[3]/label')
        return 'Municipal Data not Available'
    except NoSuchElementException:
        pass


if __name__ == '__main__':
    format_csv()

    # for zipcode in zipcodes_ma:
    #     new_main_scrape(zipcode=zipcode)
