import requests
import json
import pandas as pd
from pandas.testing import assert_frame_equal
import os
import csv
import difflib
import traceback
from pathlib import Path
from datetime import datetime
import glob
import time
from email_service import send_email
from ma.zipcodes_list import ma_zipcodes


def timeit(method):
    """
    Decorator function to time other function
    :param method:
    :return:
    """

    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts))
        else:
            print('\nRuntime for %r is %2.2f s' % (method.__name__, (te - ts)))
        return result

    return timed


def df_is_equal(df1, df2):
    """
    This is a function that uses pandas.testing to check if two dataframes are equals
    :param df1: first dataframe
    :param df2: second dataframe
    :return: bool
    """
    assert_frame_equal(left=df1, right=df2)


def check_unique():
    """
    Returns a tuple with the original merged zipcode supplier companies and the number of unique suppliers
    :return:
    """

    path = r'results_MA'  # use your path
    all_files = glob.glob(path + "/*.csv")

    li = []
    print(f"The number of zipcodes checking for unique are :: ", len(all_files))
    for filename in all_files:
        df = pd.read_csv(filename, index_col=None,
                         header=0, encoding='utf-8', float_precision='round_trip')
        li.append(df)

    df = pd.concat(li, axis=0, ignore_index=True)
    # Deleting Zipcode and Date_Downloaded columns from the Dataframe
    df.__delitem__('Zipcode')
    df.__delitem__('Date_Downloaded')
    # Changing NaN values in the df to None python
    df = df.where((pd.notnull(df)), None)
    print(df.drop_duplicates().to_string())
    # Number of rows merged
    all_df_shape = df.shape[0]
    # Number of rows unique
    unique_df_shape = df.drop_duplicates().shape[0]
    print(f"\nMerged {len(all_files)} zipcodes rows :: ", all_df_shape)
    print(f"Unqiue {len(all_files)} zipcodes rows :: ", unique_df_shape)
    return all_df_shape, unique_df_shape


def diff_checker(old_file, new_file):
    """
    Returns boolean if the two files are similar
    :param filename1: filepath for first file
    :param filename2: filepath for second file
    :return: boolean true or false
    """
    from difflib import SequenceMatcher

    text1 = open(old_file).read()
    text2 = open(new_file).read()
    for line in open(new_file).readlines()[:-2]:
        print(line)
        lineSplit = line.split(',')
        lineSplit = lineSplit.pop(17)
        print(lineSplit)
    words_text1 = text1.split(',')
    words_text2 = text2.split(',')
    # del words_text1[16::17]
    # del words_text2[16::17]
    remove_list = words_text2[17::20]
    # print(words_text1)
    # print(words_text2)
    m = SequenceMatcher(None, text1, text2)
    print(f"\t Similarity between {old_file} and {new_file} :: {m.ratio()}")
    exit()



def convert_cents_to_dollars(x):
    """
    :param x: the string value in cents
    :return: a float value in dollars
    """
    # Finding all the text before the first space
    str_val = str(x).split(' ')[0]
    if str_val == 'None':
        return 0
    if str_val:
        try:
            return float(str_val) / 100
        except ValueError:
            return 0


def get_distribution_companies(zipcode):
    """
    This function will get all TDU companies for that particular zipcode -- as part of the response
    zipcode: zipcode for MA
    :return: json response
    """
    post_data_1 = dict(customerClassId=1,
                       zipCode=str(zipcode))
    r = requests.post("http://www.energyswitchma.gov/consumers/distributioncompaniesbyzipcode",
                      data=post_data_1)
    jsonify_r = json.loads(r.text)
    # jsonify_r is a list of Python Dictionary each containing info about the TDU
    return jsonify_r


def update_tracking(zipcode: str, is_new_entry: bool, timestamp: str, filename: str):
    """
    This function updates the tracking for each zipcode
    :param zipcode: zipcode
    :param is_new_entry: if there was any changes
    :param timestamp: timestamp to put in
    :param filename: file name to put in
    :return: None
    """
    with open('track_latest.csv', 'r') as f:
        r = csv.reader(f)
        rows = list(r)
        if is_new_entry:
            rows.append([zipcode, filename, timestamp])
        else:
            for itr1, row in enumerate(rows):
                if zipcode in row:
                    rows[itr1][1] = filename
                    rows[itr1][2] = timestamp
    writer = csv.writer(open('track_latest.csv', 'w', newline=''))
    writer.writerows(rows)


def get_suppliers(zipcode):
    """
    This function loops through each of the companies returned from the get_distribution_companies
    and gets the supplier's list for each of them
    :param zipcode: zipcode
    :return: A csv file is saved, returns a Bool value if the zipcode scrape was successful or not
    """
    # Iterates over all the TDUs for that particular zipcode
    # type(dist_company) is Python Dictionary
    timestamp_start = datetime.today()
    for dist_company in get_distribution_companies(zipcode=zipcode):
        # TDU ID - internal
        company_id = dist_company['distributionCompanyId']
        # TDU Name
        company_name = dist_company['distributionCompanyName']
        # TDU is municipal
        is_municipal = dist_company['isMunicipalElectricCompany']
        # Checking if TDU is municipal, if not then proceed ...
        if not is_municipal:
            post_data = dict(customerClassId="1",
                             distributionCompanyId=str(company_id),
                             distributionCompanyName=str(company_name),
                             monthlyUsage=600,
                             zipCode=zipcode)
            # Making the second request, now to get the supplier's list for that particular TDU
            r2 = requests.post("http://www.energyswitchma.gov/consumers/compare", data=post_data)
            suppliers_list = json.loads(r2.text)
            # Creating a Dataframe (a table like format) for easier analysis and exporting to CSV
            df = pd.DataFrame.from_dict(suppliers_list)
            # Mentioning the columns we want
            df = df[['supplierName', 'pricingStructureDescription', 'pricePerMonth', 'pricePerUnit',
                     'introductoryPrice', 'introductoryPrice', 'enrollmentFee', 'contractTerm',
                     'earlyTerminationDetailExport',
                     'hasAutomaticRenewal', 'automaticRenewalDetail',
                     'renewableEnergyProductPercentage', 'renewableEnergyProductDetail',
                     'otherProductServicesDetail',
                     'isDistributionCompany', 'estimatedCost', 'otherProductServices']]
            # Adding zipcode column to the Dataframe
            df["Zipcode"] = zipcode
            # Adding timestamp column to the Dataframe
            df["Date_Downloaded"] = timestamp_start.strftime('%m/%d/%y %H:%M')
            df['TDU_Service_Territory'] = company_name
            # Change column/header names as per convention
            df.columns = ['Supplier_Name', 'Rate_Type', 'Fixed_Charge', 'Variable_Rate',
                          'Introductory_Rate',
                          'Introductory_Price_Value', 'Enrollment_Fee', 'Contract_Term',
                          'Early_Termination_Fee', 'Automatic_Renewal_Type',
                          'Automatic_Renewal_Detail',
                          'Percent_Renewable', 'Renewable_Description', 'Incentives_Special_Terms',
                          'Incumbent_Flag',
                          'Estimated_Cost', 'Other_Product_Services', 'Zipcode', 'Date_Downloaded',
                          'TDU_Service_Territory']
            # Modifying variable rate column to convert to dollars
            df['Variable_Rate'] = df['Variable_Rate'].apply(convert_cents_to_dollars)
            # Adding the introductory_rate column based on introductory_rate_value column
            df['Introductory_Rate'] = df['Introductory_Price_Value'].apply(
                lambda x: True if x else False)

            timestamp_filename_format = timestamp_start.strftime('%m%d%y_%H_%M_%S')
            file_zipcode_ci = glob.glob(f'results_MA/{zipcode}_CI{company_id}*.csv')
            print(f"\t {file_zipcode_ci}")
            zipcode_filename = f'results_MA/{zipcode}_CI{company_id}_{timestamp_filename_format}.csv'

            if len(file_zipcode_ci) > 0:
                buffer_file = "results_MA/trash.csv"
                df_buffer = df
                df_buffer.__delitem__('Date_Downloaded')
                df_buffer.__delitem__('Zipcode')

                df_buffer.to_csv(buffer_file, index=False, float_format="%.3f")
                # df_previous = pd.read_csv(file_zipcode_ci[0], float_precision='round_trip')

                diff_checker(buffer_file, file_zipcode_ci[0])

                """
                df_new = pd.read_csv("results_MA/trash.csv", float_precision='round_trip')
                
                df_previous.__delitem__('Date_Downloaded')
                df_new.__delitem__('Date_Downloaded')
                df_previous.__delitem__('Zipcode')
                df_new.__delitem__('Zipcode')

                if not df_previous.equals(df_new):
                    print("\tWriting to a new file: ", zipcode_filename)
                    df.to_csv(zipcode_filename, index=False, float_format="%.3f")
                    print("\t Updating tracking ...")
                    update_tracking(zipcode=zipcode,
                                    is_new_entry=False,
                                    timestamp=timestamp_start.strftime('%m/%d/%y %H:%M'),
                                    filename=zipcode_filename)
                else:
                    print("\t Previously scraped, no updates found.")

                """
            else:
                print("\t Writing to a new file: ", zipcode_filename)
                df.to_csv(zipcode_filename, index=False, float_format="%.3f")
                print("\t Updating tracking ...")
                update_tracking(zipcode=zipcode,
                                is_new_entry=True,
                                timestamp=timestamp_start.strftime('%m/%d/%y %H:%M'),
                                filename=zipcode_filename)

            return True
    # If something goes wrong, False is returned
    return False


@timeit
def scrape():
    """
    This is the main function to scrape the results
    :return: None
    """
    # Creates a file if it does not exist to append the timestamp of each script run

    if not Path('track_latest.csv').is_file():
        print("Tracking file does not exist, creating one ... ")
        with open('track_latest.csv', 'w', newline='') as f:
            # writer = csv.writer(f)
            f.write("Zipcode, Latest_File, Last_Updated")

    success = 0

    # Formats the zipcodes in the right format
    zipcodes_ma_0 = list(set(map(lambda x: '0' + str(x), ma_zipcodes)))
    # [ACTION REQUIRED] Set the number of zipcodes you want to run the script for
    runnable_zipcdes = zipcodes_ma_0[:100]
    print(f"Number of zipcodes running for: {len(runnable_zipcdes)}")
    runnable_zipcdes = ["01005"]

    for zip in runnable_zipcdes:
        print("Running for zipcode:", zip)
        if get_suppliers(zipcode=str(zip)):
            success += 1

    if not Path('run_history.txt').is_file():
        with open('run_history.txt', 'w') as run_file:
            run_file.write(datetime.today().strftime('%m/%d/%y %H:%M:%S') + f", {success}")
    else:
        with open('run_history.txt', 'a', newline='') as run_file:
            run_file.write("\n" + datetime.today().strftime('%m/%d/%y %H:%M:%S') + f", {success}")

    if Path('results_MA/trash.csv').is_file():
        os.remove('results_MA/trash.csv')

    # The success variable to see how many zipcodes were actually extracted
    print(f'The number of zipcodes successfully scraped are: {success}')


scrape()
# try:
#     # [ACTION REQUIRED] Select which function you want to run
#     scrape()
#     # check_unique()
# except Exception as err:
#     # Send email
#     error_traceback = traceback.extract_tb(err.__traceback__)
#     send_email(body=f"Traceback at {datetime.today().strftime('%m/%d/%y %H:%M:%S')} from Scheduler: {error_traceback}")
