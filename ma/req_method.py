import requests
import json
import pandas as pd
import os
import csv
import sys
import traceback
from pathlib import Path
from datetime import datetime
import glob
import time
import re
from ma.zipcodes_list import ma_zipcodes
from csv_diff import load_csv, compare
from email_service import send_email

dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(Path(dir_path).parent)
sys.path.append(os.getcwd())
sys.path.append(dir_path)
os.chdir(dir_path)


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


def check_unique():
    """
    Returns a tuple with the original merged zipcode supplier companies and the number of
    unique suppliers.
    :return:
    """

    path = r'results_MA'
    all_files = glob.glob(path + "/*.csv")

    li = []
    print(f"The number of zipcodes checking for unique are :: ", len(all_files))
    for filename in all_files:
        df = pd.read_csv(filename, index_col=None,
                         header=0, encoding='utf-8',
                         float_precision='round_trip')
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
    r = requests.post(
        "http://www.energyswitchma.gov/consumers/distributioncompaniesbyzipcode",
        data=post_data_1)
    jsonify_r = json.loads(r.text)
    # jsonify_r is a list of Python Dictionary each containing info about the TDU
    return jsonify_r


def update_tracking(zipcode: str, is_new_entry: bool, timestamp: str,
                    filename: str):
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
            r2 = requests.post(
                "http://www.energyswitchma.gov/consumers/compare",
                data=post_data)
            suppliers_list = json.loads(r2.text)
            # Creating a Dataframe (a table like format) for easier analysis and exporting to CSV
            df = pd.DataFrame.from_dict(suppliers_list)
            # Mentioning the columns we want
            df = df[
                ['supplierName', 'pricingStructureDescription', 'pricePerMonth',
                 'pricePerUnit',
                 'introductoryPrice', 'introductoryPrice', 'enrollmentFee',
                 'contractTerm',
                 'earlyTerminationDetailExport',
                 'hasAutomaticRenewal', 'automaticRenewalDetail',
                 'renewableEnergyProductPercentage',
                 'renewableEnergyProductDetail',
                 'otherProductServicesDetail',
                 'isDistributionCompany', 'estimatedCost',
                 'otherProductServices']]
            # Adding zipcode column to the Dataframe
            df["Zipcode"] = zipcode
            # Adding timestamp column to the Dataframe
            df["Date_Downloaded"] = timestamp_start.strftime('%m/%d/%y %H:%M')
            df['TDU_Service_Territory'] = company_name
            # Change column/header names as per convention
            df.columns = ['Supplier_Name', 'Rate_Type', 'Fixed_Charge',
                          'Variable_Rate',
                          'Introductory_Rate',
                          'Introductory_Price_Value', 'Enrollment_Fee',
                          'Contract_Term',
                          'Early_Termination_Fee', 'Automatic_Renewal_Type',
                          'Automatic_Renewal_Detail',
                          'Percent_Renewable', 'Renewable_Description',
                          'Incentives_Special_Terms',
                          'Incumbent_Flag',
                          'Estimated_Cost', 'Other_Product_Services', 'Zipcode',
                          'Date_Downloaded',
                          'TDU_Service_Territory']
            # Modifying variable rate column to convert to dollars
            df['Variable_Rate'] = df['Variable_Rate'].apply(
                convert_cents_to_dollars)
            # Adding the introductory_rate column based on introductory_rate_value column
            df['Introductory_Rate'] = df['Introductory_Price_Value'].apply(
                lambda x: True if x else False)

            timestamp_filename_format = timestamp_start.strftime(
                '%m%d%y_%H_%M_%S')
            zipcode_filename = f'results_MA/{zipcode}_CI{company_id}_{timestamp_filename_format}.csv'
            file_zipcode_ci = glob.glob(
                    f'results_MA/{zipcode}_CI{company_id}*.csv')
            
            # If this is not the first time the file was written, check for plan updates
            if len(file_zipcode_ci) > 0:
                # Identify the most recent filename
                date_regex = re.compile("\d{6}")
                date_num_list = []
                for row in file_zipcode_ci:
                    date = date_regex.findall(row)[0]
                    date_num = int(date[4:6]+date[0:4])
                    date_num_list.append(date_num)
                filename_prev = file_zipcode_ci[date_num_list.index(max(date_num_list))]
            
                # Check whether there have been any plan updates since the last data pull
                df.to_csv("results_MA/trash.csv", index=False, float_format="%.5f")
                df_new = pd.read_csv("results_MA/trash.csv")
                df_new.__delitem__('Date_Downloaded')
                df_new.__delitem__('Zipcode') 
                df_new.fillna(value=pd.np.nan, inplace=True)
                df_new = df_new.replace(r'^\s*$', pd.np.nan, regex=True)
                df_new = df_new.replace('\\n|\\r|\s','', regex=True)
                df_new['Key'] = df_new.apply(
                    lambda row: '_'.join(row.values.astype(str)), axis=1)
                df_new.to_csv("results_MA/trash.csv", index=False,
                              float_format="%.5f")
                
                df_previous = pd.read_csv(filename_prev)
                df_previous.__delitem__('Date_Downloaded')
                df_previous.__delitem__('Zipcode') 
                df_previous.fillna(value=pd.np.nan, inplace=True)
                df_previous = df_previous.replace(r'^\s*$', pd.np.nan, regex=True)
                df_previous = df_previous.replace('\\n|\\r|\s','', regex=True)
                df_previous['Key'] = df_previous.apply(
                    lambda row: '_'.join(row.values.astype(str)), axis=1)
                df_previous.to_csv("results_MA/trash_old.csv", index=False,
                                   float_format="%.5f")
                
                diff = compare(load_csv(
                        open("results_MA/trash_old.csv"), key="Key"), load_csv(
                                open("results_MA/trash.csv"), key="Key"))
                
                #df_previous = pd.read_csv(file_zipcode_ci[0], float_precision='round_trip')
                #df_new = pd.read_csv("results_MA/trash.csv", float_precision='round_trip')

                if (diff['added'] == []) and (diff['removed'] == []) and (diff['changed'] == []):
                    print("\t Previously scraped, no updates found.")
                else:
                    print("\tWriting to a new file: ", zipcode_filename)
                    df.to_csv(zipcode_filename, index=False, float_format="%.5f")
                    print("\t Updating tracking ...")
                    update_tracking(zipcode=zipcode,
                                    is_new_entry=False,
                                    timestamp=timestamp_start.strftime('%m/%d/%y %H:%M'),
                                    filename=zipcode_filename)

            else:
                print("\t Writing to a new file: ", zipcode_filename)
                df.to_csv(zipcode_filename, index=False, float_format="%.5f")
                print("\t Updating tracking ...")
                update_tracking(zipcode=zipcode,
                                is_new_entry=True,
                                timestamp=timestamp_start.strftime(
                                    '%m/%d/%y %H:%M'),
                                filename=zipcode_filename)

            return True
    # If something goes wrong, False is returned
    return False


@timeit
def scrape():
    """
    This is the main function to scrape the results.
    :return: None.
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
    #runnable_zipcdes = zipcodes_ma_0[:100]
    runnable_zipcdes = zipcodes_ma_0
    print(f"Number of zipcodes running for: {len(runnable_zipcdes)}")

    for zip in runnable_zipcdes:
        print("Running for zipcode:", zip)
        if get_suppliers(zipcode=str(zip)):
            success += 1

    if not Path('run_history.txt').is_file():
        with open('run_history.txt', 'w') as run_file:
            run_file.write(
                datetime.today().strftime('%m/%d/%y %H:%M:%S') + f", {success}")
    else:
        with open('run_history.txt', 'a', newline='') as run_file:
            run_file.write("\n" + datetime.today().strftime(
                '%m/%d/%y %H:%M:%S') + f", {success}")

    if Path('results_MA/trash.csv').is_file():
        os.remove('results_MA/trash.csv')
        
    if Path('results_MA/trash_old.csv').is_file():
        os.remove('results_MA/trash_old.csv')

    # The success variable to see how many zipcodes were actually extracted
    print(f'The number of zipcodes successfully scraped are: {success}')


try:
    # [ACTION REQUIRED] Select which function you want to run
    scrape()
    check_unique()
except Exception as err:
    error_traceback = traceback.extract_tb(err.__traceback__)
    send_email(body=f"Traceback at {datetime.today().strftime('%m/%d/%y %H:%M:%S')} from Scheduler: {error_traceback}")
