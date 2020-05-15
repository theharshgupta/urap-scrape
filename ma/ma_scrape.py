# from scrape import get_zipcodes, ma_download_dir, driver, NoSuchElementException
from selenium.common.exceptions import NoSuchElementException

from newyork.scrape import get_zipcodes
from selenium import webdriver
from pathlib import Path
from datetime import datetime
import csv
import time
import os
import pandas as pd

STATE = 'Massachusetts'
MA_ZIPCODE_LEVEL = 'ma_zipcode_level.csv'
ZIPCODE_LEVEL_HEADERS = ['State', 'Zipcode', 'Website', 'TDU_Service_Territory', 'Pricing_Range',
                            'Minimum_Monthly_Cost', 'Maximum_Monthly_Cost', 'Minimum_Contract_Term',
                            'Maximum_Contract_Term', 'Date_Downloaded', 'Default_Monthly_kWh']
BASE_URL = 'http://www.energyswitchma.gov/#/'
min_contract_term = None
zipcodes_ma = get_zipcodes('MA')
zipcodes_ma = list(map(lambda x: '0' + str(x), zipcodes_ma))


def get_datetime():
    """
    Function to return current datetime in format MM/DD/YYYY HH:MM
    :return: the string of current datetime
    """
    return datetime.today().strftime('%m/%d/%y %H:%M:%S')


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


def convert_cents_to_dollars(x):
    """
    :param x: the string value in cents
    :return: a float value in dollars
    """
    str_val = str(x).split(' ')[0]
    if str_val == 'None':
        return 0
    if str_val:
        return float(str_val) / 100


def format_csv():
    """
    Extracts the useful information from the downloaded csv from the ma_downloads folder in the root directory
    and formats it
    :return: formatted csv is saved to the ma_csv folder, creates a zip code level csv in the root dir too
    """
    # Here we initialise all the zipcode level fields to None so that it doesnt throw error for
    # not found
    service_territory = None
    min_monthly_cost = None
    max_monthly_cost = None
    min_contract_term = None
    max_contract_term = None
    product_sorting = None
    supplier_list = None
    pricing = None
    default_monthly_kWh = None
    # Iterating through each file in the ma_downloads folder
    for file in os.listdir('ma_downloads'):
        # Initialize the data row to None
        data_zipcode_level = None
        # Opening the file
        with open('ma_downloads/' + file) as csv_file:
            # initializing the csv reader
            reader = csv.reader(csv_file)
            # converting the iterator reader to a list
            csv_list = list(reader)
        # checking if the csv_list variable is not empty
        if csv_list:
            # extracting the default monthly kwH from the last line of the csv
            if 'zckharsh' in csv_list[-1]:
                default_monthly_kWh = csv_list[-1][-1]
            # iterating through each of the line of the csv
            for index, line in enumerate(csv_list):
                # making sure that the line is not empty or nothing is present in a line
                if len(line) > 0:
                    # checking if column label is present in the line, if it is then assign it to it
                    if 'Service Territory' in line[0]:
                        service_territory = line[-1]
                    if 'Pricing' in line[0]:
                        pricing = line[-1]
                    if 'Minimum Monthly cost' in line[0]:
                        min_monthly_cost = line[-1]
                    if 'Maximum Monthly cost' in line[0]:
                        max_monthly_cost = line[-1]
                    if 'Minimum Contract Term' in line[0]:
                        min_contract_term = line[-1]
                    if 'Maximum Contract Term' in line[0]:
                        max_contract_term = line[-1]
                    # Finally extracting the supplier information and saving it to the supplier list
                    if len(line) > 0:
                        if line[0] == 'Supplier Name':
                            # We are slicing the original csv_list of all the lines to extract the lines with only the
                            # supplier information/ plans (last line contains default monthly kWh)
                            supplier_list = csv_list[index:-1]
                            # breaks out of the loop if it finds the supplier list line
                            break
            # creates a list of labels, the second item in this list is extracting the zipcode from the filename
            data_zipcode_level = [STATE, str(file).split('.')[0].split('_')[-1], BASE_URL, service_territory, pricing,
                                  min_monthly_cost, max_monthly_cost, min_contract_term, max_contract_term,
                                  get_datetime(), default_monthly_kWh]

        # Saving the things to the CSV

        # initialising the header_exists to default false
        header_exists = False
        # checking if the ma_zipcode_level file csv is present
        if Path(MA_ZIPCODE_LEVEL).is_file():
            # if present, we open and see if headers are present
            with open(MA_ZIPCODE_LEVEL, 'r') as read_csv:
                if 'Zipcode' in read_csv.readline():
                    # if headers are there, we change the variable value of header_exist
                    header_exists = True
        # we open the file in append mode. newline='' is important to ignore random lines
        with open(MA_ZIPCODE_LEVEL, 'a', newline='') as csv_file:
            # creating a writer
            writer = csv.writer(csv_file)
            # if headers dont exist we write the headers
            if not header_exists:
                writer.writerow(ZIPCODE_LEVEL_HEADERS)
            # write the rows
            if data_zipcode_level:
                writer.writerow(data_zipcode_level)

        # Plan Level CSV creation
        df = pd.DataFrame.from_records(supplier_list)
        # df.columns = list(df.values.tolist())[0]
        df = df[1:]
        # Labels of the dataframe
        df.columns = ['Supplier_Name', 'Rate_Type', 'Fixed_Charge', 'Variable_Rate',
                      'Introductory_Rate', 'Enrollment_Fee', 'Contract_Term',
                      'Early_Termination_Fee', 'Automatic_Renewal_Type',
                      'Percent_Renewable', 'New_Regional_Resources', 'Incentives_Special_Terms',
                      'Est_Monthly_Bill_Default']
        # gets the current date and time in specific format
        df['Date_Downloaded'] = get_datetime()
        df['Incumbent_Flag'] = False
        # the first plan is True for incumbent flag
        df.at[1, 'Incumbent_Flag'] = True
        df['Plan_Order_Rank'] = df.index
        # convert the cents value to dollars for variable rate
        df['Variable_Rate'] = df['Variable_Rate'].apply(convert_cents_to_dollars)
        # saving the dataframe to a csv in the ma_csvs folder
        df.to_csv(f'ma_csvs/{file}', index=False)


def new_main_scrape(zipcode):
    """
    This function just goes to the url for the specific zipcode and then clicks on the download button.
    The downloaded file is then edited -- renamed and saved to a specific folder
    :param zipcode: the specific zipcode for MA
    :return: nothing
    """
    driver = webdriver.Chrome("C:\chromedriver.exe")
    # URL for a specific zipcode
    url_ma_recur = f'http://www.energyswitchma.gov/#/compare/2/1/{zipcode}/'
    # Calling the web browser on that specific url
    driver.get(url_ma_recur)
    # waiting for the page to load
    time.sleep(1)

    # Getting the Default_Monthly_kWh
    try:
        xpath = '/html/body/div[2]/ui-view/product-compare/div[1]/div[2]/div/div[2]/div/div/input'
        default_monthly_kWh = driver.find_element_by_xpath(xpath).get_attribute('value')
    except NoSuchElementException:
        # if value is not fetched for some reason, program should not stop, the default set None
        default_monthly_kWh = None

    # clicking on the download button
    xpath_button = '/html/body/div[2]/ui-view/product-compare/div[2]/div/div[4]/button'
    download_to_csv_button = driver.find_element_by_xpath(xpath_button)
    download_to_csv_button.click()

    time.sleep(1)
    # file renaming
    if Path(f'ma_downloads/ma_{zipcode}.csv').is_file():
        # This means that the file already exists, however it replaces that file with the new file
        print(f"ERROR: File already exists in the downloaded folder for the zipcode {zipcode}")

    # otherwise we rename the downloaded file, overwriting that
    downloaded_filename = ma_download_dir + f'EnergySwitchMass_{datetime.today().month}{datetime.today().day}{datetime.today().year}.csv'
    if Path(downloaded_filename).is_file():
        os.rename(
            ma_download_dir + f'EnergySwitchMass_{datetime.today().month}{datetime.today().day}{datetime.today().year}.csv',
            ma_download_dir + f'ma_{zipcode}.csv')

        # we add the default monthly kWh field to the bottom of the downloaded csv so that the format_csv function can
        # fetch it and use it in column labels.
        with open(ma_download_dir + f'ma_{zipcode}.csv', 'a') as update_file:
            update_file.write(f'zckharsh, {default_monthly_kWh}')
    print(f"Successfully downloaded for {zipcode}")


def old_mainsite_scrape(zipcode):
    """
    DEPRECATED - Now using the new approach using requests module
    :param zipcode: zipcode
    :return: nothing
    """
    driver = webdriver.Chrome("C:\chromedriver.exe")
    driver.get(BASE_URL)
    print("Zipcode: ", zipcode)

    # clicking the home radio button
    driver.find_element_by_xpath(
        '/html/body/div[2]/ui-view/home/div[1]/div[1]/div/div[2]/div/fieldset/form/div['
        '1]/div/div[1]/label/input').click()
    zipcode_input = driver.find_element_by_xpath(
        '/html/body/div[2]/ui-view/home/div[1]/div[1]/div/div[2]/div/fieldset/form/div['
        '2]/div/input')

    # we clear the input field where we have to put the zipcode
    zipcode_input.clear()
    # we input the zipcode into the field
    zipcode_input.send_keys(zipcode)
    # we click the START SHOPPING button
    driver.find_element_by_xpath('/html/body/div[2]/ui-view/home/div[1]/div[1]/div/div['
                                 '2]/div/fieldset/form/div[2]/div/button').click()
    time.sleep(1)
    # now checking if 'my electric company is' thing pops up
    try:
        try:
            button_continue_shopping = driver.find_element_by_xpath(
                '/html/body/div[2]/ui-view/home/div[1]/div[1]/div/div[2]/div/fieldset/form/div[4]/div/button')
            dropdown_options = driver.find_element_by_xpath('//*[@id="distributionCompanyId"]').find_elements_by_tag_name('option')
            print('\t Dropdown options:', dropdown_options)

            for index, option in enumerate(dropdown_options):
                if '<Select>' != option.get_attribute('label'):
                    print("\t Option:", option)
                    print("\t Clicking the option ...")
                    option.click()
                    time.sleep(1)
                    button_continue_shopping.click()
                    driver.get(BASE_URL)

                    driver.find_element_by_xpath('/html/body/div[2]/ui-view/home/div[1]/div[1]/div/div[2]/div/fieldset/form/div[1]/div/div[1]/label/input').click()
                    zipcode_input = driver.find_element_by_xpath('/html/body/div[2]/ui-view/home/div[1]/div[1]/div/div[2]/div/fieldset/form/div[2]/div/input')

                    # we clear the input field where we have to put the zipcode
                    zipcode_input.clear()
                    # we input the zipcode into the field
                    zipcode_input.send_keys(zipcode)
                    # we click the START SHOPPING button
                    driver.find_element_by_xpath('/html/body/div[2]/ui-view/home/div[1]/div[1]/div/div['
                                                 '2]/div/fieldset/form/div[2]/div/button').click()
                    time.sleep(1)



        except NoSuchElementException as no_dropdown_error:
            print("\t The dropdown is not present, hence proceeding ...")

    except Exception as e:
        print("\t Error during execution and scrape fro MA")
        error_message = f"Error occurred while running the scrape for MA: \n\n {e}"
        raise e
        # send_email(body=error_message)
        pass


# We use __name__ == '__main__' to make sure that the functions dont run even when something from
# this file is imported in some other py file
if __name__ == '__main__':
    for zipcode in zipcodes_ma[:]:
        old_mainsite_scrape(zipcode=zipcode)


