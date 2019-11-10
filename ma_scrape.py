from scrape import get_zipcodes, ma_download_dir, driver, NoSuchElementException
from datetime import datetime
from pathlib import Path
from datetime import datetime
import csv
import time
import os
import pandas as pd
from email_service import send_email

zipcodes_ma = get_zipcodes('MA')
state = 'Massachusetts'
zipcodes_ma = list(map(lambda x: '0' + str(x), zipcodes_ma))
print(zipcodes_ma)
ma_zipcode_level = 'ma_zipcode_level.csv'

ma_zipcode_level_headers = ['State', 'Zipcode', 'Website', 'Service Territory', 'Customer Class', 'Pricing',
                            'Contract Term', 'Minimum Monthly Cost',
                            'Maximum Monthly Cost', 'Minimum Contract Term', 'Maximum Contract Term', 'Date Downloaded']
url_ma = 'http://www.energyswitchma.gov/#/'

min_contract_term = None


def get_datetime():
    return datetime.today().strftime('%m/%d/%y %H:%M')


def check_unqiue():
    massive_data = []
    i = 0
    for file in os.listdir('ma_csvs'):
        print(file)
        with open('ma_csvs/' + file) as csv_file:
            reader = csv.reader(csv_file)
            csv_list = list(reader)[1:]
            print(csv_list)
            if i == 0:
                massive_data.append(csv_list)
                i = i + 1
            else:
                csv_list = csv_list[1:]
                massive_data.append(csv_list)


def format_csv():
    """
    Extracts the useful information from the csv and formats it into the correct format
    :return: formatted csv is saved to the ma_csv folder
    """
    global service_territory, customer_class, contract_term, min_monthly_cost, max_monthly_cost, min_contract_term, max_contract_term, product_sorting, supplier_list, pricing
    for file in os.listdir('ma_downloads'):
        data_zipcode_level = None
        print(file)
        with open('ma_downloads/' + file) as csv_file:
            reader = csv.reader(csv_file)
            csv_list = list(reader)
        if csv_list:
            for index, line in enumerate(csv_list):
                if len(line) > 0:
                    if 'Service Territory' in line[0]:
                        service_territory = line[-1]
                    if 'Customer Class' in line[0]:
                        customer_class = line[-1]
                    if 'Pricing' in line[0]:
                        pricing = line[-1]
                    if 'Contract Term' in line[0]:
                        contract_term = line[-1]
                    if 'Minimum Monthly cost' in line[0]:
                        min_monthly_cost = line[-1]
                    if 'Maximum Monthly cost' in line[0]:
                        max_monthly_cost = line[-1]
                    if 'Minimum Contract Term' in line[0]:
                        min_contract_term = line[-1]
                    if 'Maximum Contract Term' in line[0]:
                        max_contract_term = line[-1]
                    if len(line) > 0:
                        if line[0] == 'Supplier Name':
                            supplier_list = csv_list[index:]
                            break
            data_zipcode_level = [state, str(file).split('.')[0], url_ma, service_territory, customer_class, pricing,
                                  contract_term, min_monthly_cost,
                                  max_monthly_cost, min_contract_term, max_contract_term, get_datetime()]

        # Saving the things to the CSV
        header_exists = False
        if Path(ma_zipcode_level).is_file():
            with open(ma_zipcode_level, 'r') as read_csv:
                if 'Zipcode' in read_csv.readline():
                    header_exists = True
        with open(ma_zipcode_level, 'a', newline='') as csv_file:
            writer = csv.writer(csv_file)
            if not header_exists:
                writer.writerow(ma_zipcode_level_headers)
            if data_zipcode_level:
                writer.writerow(data_zipcode_level)

        df = pd.DataFrame.from_records(supplier_list)
        df.columns = list(df.values.tolist())[0]
        df = df[1:]
        df.columns = ['Supplier_Name', 'Pricing Structure', 'TDU_Fixed_Charge', '' ]
        df['Date_Downloaded'] = get_datetime()
        df['Incumbent_Flag'] = True

        df.to_csv(f'ma_csvs/{file}', index=False)


def new_main_scrape(zipcode):
    """
    This function just goes to the url for the specific zipcode and then clicks on the download button.
    The downloaded file is then edited -- renamed and saved to a specific folder
    :param zipcode:
    :return:
    """
    # URL for a specific zipcode
    url_ma_recur = f'http://www.energyswitchma.gov/#/compare/2/1/{zipcode}/'
    # Calling the web browser on that specific url
    driver.get(url_ma_recur)
    # waiting for the page to load
    time.sleep(1)
    # clicking on the download button
    download_to_csv_button = driver.find_element_by_xpath(
        '/html/body/div[2]/ui-view/product-compare/div[2]/div/div[4]/button')
    download_to_csv_button.click()
    # sleeping again for 2 seconds
    time.sleep(1)
    # file renaming
    if Path(f'ma_downloads/ma_{zipcode}.csv').is_file():
        # This means that the file already exists
        print(f"ERROR: File already exists in the downloaded folder for the zipcode {zipcode}")

    # otherwise we rename the downloaded file
    os.rename(
        ma_download_dir + f'EnergySwitchMass_{datetime.today().month}{datetime.today().day}{datetime.today().year}.csv',
        ma_download_dir + f'ma_{zipcode}.csv')
    print(f"Successfully downloaded for {zipcode}")


def main_scrape(zipcode):
    """
    Going to the main page and then clicking all the radio buttons
    :param zipcode:
    :return:
    """
    driver.get(url_ma)

    driver.find_element_by_xpath('/html/body/div[2]/ui-view/home/div[1]/div[1]/div/div[2]/div/fieldset/form/div['
                                 '1]/div/div[1]/label/input').click()
    time.sleep(1)
    zipcode_input = driver.find_element_by_xpath('/html/body/div[2]/ui-view/home/div[1]/div[1]/div/div['
                                                 '2]/div/fieldset/form/div[2]/div/input')

    zipcode_input.clear()
    # Inputting the zipcodes
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
    check_unqiue()
    driver.quit()

    # for zipcode in zipcodes_ma[:50]:
    #     new_main_scrape(zipcode=zipcode)
