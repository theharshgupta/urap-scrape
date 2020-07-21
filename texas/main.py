import os
import sys
from pathlib import Path
import csv
import pickle
import traceback
import pathlib
import pandas as pd
from datetime import datetime
import requests
from requests.exceptions import Timeout
import json
import urllib.request
import logging
from tqdm import tqdm
from csv_diff import load_csv, compare
import numpy as np

dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(Path(dir_path).parent)
sys.path.append(os.getcwd())
sys.path.append(dir_path)

from email_service_TX import send_email
import texas.pdf as pdf
import texas.utils as utils
import texas.map_zipcodes as map_zips
# [2014, 19775, 21834, 21983, 22018, 22029, 22544, 23515, 23753, 23517, 22549, 22039, 22013, 21993, 19776, 11371, 9721, 18736, 22006, 22016, 22027, 22543, 22469, 23442, 23513, 23960, 9581, 18735, 20186, 23514, 22545, 22210, 22032, 21986, 22034, 22120, 22547, 23516, 19777, 19785]
# [59, 19775, 21834, 21983, 22018, 22029, 22544, 23515, 23753, 23517, 22549, 22039, 22013, 21993, 19776, 11371, 9721, 18736, 22006, 22016, 22027, 22543, 22469, 23442, 23513, 23960, 9581, 18735, 20186, 23514, 22545, 22210, 22032, 21986, 22034, 22120, 22547, 23516, 19777, 19785]

os.chdir(dir_path)

logging.basicConfig(format="%(asctime)s: %(message)s")


class Plan:

    def __init__(self, row_data):
        """
        Constructor for the class for the Plan
        :param row_data: type Python dictionary
        """
        self.id_key = row_data.get("[idKey]")
        self.tdu_company_name = row_data.get("[TduCompanyName]")
        self.rep_company = row_data.get("[RepCompany]")
        self.product = row_data.get("[Product]")
        self.kwh500 = row_data.get("[kwh500]")
        self.kwh1000 = row_data.get("[kwh1000]")
        self.kwh2000 = row_data.get("[kwh2000]")
        self.fees_credits = row_data.get("[Fees/Credits]")
        self.pre_paid = row_data.get("[PrePaid]")
        self.time_of_use = row_data.get("[TimeOfUse]")
        self.fixed = row_data.get("[Fixed]")
        self.rate_type = row_data.get("[RateType]")
        self.renewable = row_data.get("[Renewable]")
        self.term_value = row_data.get("[TermValue]")
        self.cancel_fee = row_data.get("[CancelFee]")
        self.website = row_data.get("[Website]")
        self.special_terms = row_data.get("[SpecialTerms]")
        self.terms_url = row_data.get("[TermsURL]")
        self.promotion = row_data.get("[Promotion]")
        self.promotion_desc = row_data.get("[PromotionDesc]")
        self.facts_url = row_data.get("[FactsURL]")
        self.enroll_url = row_data.get("[EnrollURL]")
        self.prepaid_url = row_data.get("[PrepaidURL]")
        self.enroll_phone = row_data.get("[EnrollPhone]")
        self.new_customer = row_data.get("[NewCustomer]")
        self.min_usage_fees_credits = row_data.get("[MinUsageFeesCredits]")
        self.language = row_data.get("[Language]")
        self.rating = row_data.get("[Rating]")
        self.zipcodes = []

    def equals(self, plan2):
        """
        Compare two plans.
        :param plan2: The other plan.
        :return: True or false.
        """
        if self.id_key == plan2.id_key:
            return True


def combine_results():

    """
    This subroutine will be run after the PDF downloading is finished and before the zipcode mapping
    process has started. Combines the new-plans.csv and result.csv files.
    :return: None
    """
    # Read in new/updated plans
    updated_plans = pd.read_csv(utils.NEW_PLANS_RESULT_CSV)
    updated_plan_ids = updated_plans['[idKey]'].values
    
    # Identify all currently active Plan IDs
    current_plans = pd.read_csv(utils.LATEST_CSV_PATH)
    current_plan_ids = current_plans['[idKey]'].values
    
    # Combine updated plans with plans that were not updated or deleted since last scrape
    if not utils.exists(utils.RESULT_CSV):
        merged2 = updated_plans
        send_email(
            body=f"Warning: result.csv does not exist",
            files = [utils.LOGS_PATH])
    else:
        result = pd.read_csv(utils.RESULT_CSV)
        old = result.loc[(~result['[idKey]'].isin(updated_plan_ids)) & 
                         (result['[idKey]'].isin(current_plan_ids))]
        merged = pd.DataFrame(old).append(updated_plans)
        #print(merged.to_string())
        
        # Update PDF filepaths for any plans that have not been updated but have newly downloaded EFLs
        check_plans = pd.read_csv(utils.CHECK_PLANS_RESULT_CSV)
        check_plans = check_plans[['[FactsURL]','pdf_filepath']]
        check_plans.columns = ['[FactsURL]','pdf_filepath2']
        merged2 = merged.merge(check_plans, on='[FactsURL]', how='left')
        merged2['pdf_filepath3'] = np.where((merged2['pdf_filepath2']).isna(), merged2['pdf_filepath'], merged2['pdf_filepath2'])
        merged2.drop(['pdf_filepath', 'pdf_filepath2'], axis=1, inplace=True)
        merged2.rename(columns={'pdf_filepath3':'pdf_filepath'}, inplace=True)
    
    # Check for any missing/extra plans
    if len(current_plans.index) != len(merged2.index):
        result_plan_ids = result['[idKey]'].values
        test = current_plans.loc[~current_plans['[idKey]'].isin(result_plan_ids)]
        test2 = merged2.loc[~merged2['[idKey]'].isin(current_plan_ids)]
        if len(test.index) > 0:
            send_email(
                body="There are plan ID(s) in the raw CSV downloaded from PowerToChoose that are not in the outputs",
                files=[utils.LOGS_PATH])
        if len(test2.index) > 0:
            send_email(
                body="There are plan ID(s) in the outputs that are not in the raw CSV downloaded from PowerToChoose",
                files=[utils.LOGS_PATH])
    
    # Export to CSV
    merged2.to_csv(utils.RESULT_CSV, index=False)
    print("Find your results at:", utils.RESULT_CSV)


def download(csv_filepath, output_fname):
    """
    Alan Comments: df2 is a slight variation of the df object above (I think?) We're iterating
    over each of the plans in df2, using their FactsURL to download the pdfs (with idKey as the
    name)

    :param csv_filepath:
    :return:
    """
    df = pd.read_csv(csv_filepath)
    data_dict = df.to_dict('records')
    result = []
    for d in tqdm(data_dict, desc="PDF Downloading", disable=True):
        plan = Plan(d)
        logging.info(f"Checking PDF for {plan.id_key} at {plan.facts_url}")
        try:
            pdf_filepath = pdf.download_pdf(pdf_url=plan.facts_url, plan=plan)
        except Exception as e:
            error_traceback = traceback.extract_tb(e.__traceback__)
            send_email(
                body=f"Error in PDF downloading while attempting to download from {plan.facts_url} \n Traceback at {utils.get_datetime()}:\n{error_traceback}",
                files=[utils.LOGS_PATH])
        if pdf_filepath:
            d['pdf_filepath'] = pdf_filepath
        else:
            d['pdf_filepath'] = "None"
        result.append(d)
    df = pd.DataFrame(result)
    df.to_csv(os.path.join(utils.RESULT_DIR, output_fname), index=False)
    print(df.to_string())


def setup():
    """
    Sets up the folders for all functions to run.
    :return: None.
    """
    print("Running the presetupm to check for folders and create them ...")
    if not utils.exists(utils.DATA_DIR):
        os.mkdir(utils.DATA_DIR)
    if not utils.exists(utils.PDF_DIR):
        os.mkdir(utils.PDF_DIR)
    if not utils.exists(utils.LOGS_DIR):
        os.mkdir(utils.LOGS_DIR)
    if not utils.exists(utils.RESULT_DIR):
        os.mkdir(utils.RESULT_DIR)
    if not utils.exists(utils.PLANS_DIR):
        os.mkdir(utils.PLANS_DIR)
    if not utils.exists(utils.MASTER_DIR):
        os.mkdir(utils.MASTER_DIR)
    if utils.exists(utils.LOGS_PATH):
        os.remove(utils.LOGS_PATH)
    if not utils.exists(utils.CSV_DIR):
        os.mkdir(utils.CSV_DIR)

    if utils.exists(utils.DIFFPLANS_CSV_PATH):
        os.remove(utils.DIFFPLANS_CSV_PATH)

    print("\tSetup completed. ")


def auto_download_csv(url):
    """
    Download raw CSV from PTC website. The function makes sure that a diffPlans.csv is
    created that contains all the plans that need to be "considered" -- i.e. to be downloaded,
    worked with, mapped, etc.
    :param url: URL to make a request.
    :return: Dataframe of new plans else None.
    """
    print("\nRunning Auto Download CSV to download the MASTER CSV...")
    filepath = f"{os.path.join(utils.MASTER_DIR, utils.get_datetime().replace('_', '-'))}.csv"

    urllib.request.urlretrieve(url, filepath)
    utils.filter_csv(csv_filepath=filepath)

    # If latest.csv file does not exist, then rename the file downloaded to latest.csv
    if not utils.exists(utils.LATEST_CSV_PATH):
        utils.copy(filepath, utils.LATEST_CSV_PATH)
        utils.copy(utils.LATEST_CSV_PATH, utils.DIFFPLANS_CSV_PATH)
        print("\tLatest CSV file did not exists, so all plans will be added. ")
        df = pd.read_csv(filepath)
        return df
    else:
        # DOUBT - does it return new plans that were added to the new csv
        diff_plans = diff_check(latest=utils.LATEST_CSV_PATH, other=filepath)
        print(diff_plans)
        if not diff_plans:
            os.remove(filepath)
            print('No new plans, so recently downloaded MASTER file was deleted.')
            return
        else:
            # Gets CSV rows that have changed in a Pandas Dataframe.
            df = pd.read_csv(filepath)
            df = df.loc[df['[idKey]'].isin(diff_plans)]
            print(df.to_string())
            utils.copy(filepath, utils.LATEST_CSV_PATH)
            df.to_csv(utils.DIFFPLANS_CSV_PATH, index=False)
            print("\tAdding different plans to DIFF plans CSV.")
            return df


def diff_check(latest, other):
    """
    Checks for differences between the last downloaded CSV and the newly
    downloaded one, deleting the new one if there are no differences.
    """
    new = pd.read_csv(latest)
    old = pd.read_csv(other)
    diff_plans = []
    for i in range(len(new)):
        latestRow = new.iloc[i]
        idKey = new.iloc[i][0]
        try:
            otherRow = old.loc[old['[idKey]'] == idKey].squeeze()
            for c in range(len(latestRow)):
                if isinstance(latestRow[c], float):
                    val_new = round(latestRow[c], 6)
                    val_old = round(otherRow[c], 6)
                else:
                    val_new = latestRow[c]
                    val_old = otherRow[c]
                if str(val_new) != str(val_old):
                    diff_plans.append(idKey)
                    break
        except Exception as err:
            diff_plans.append(idKey)
            print(err)
    return diff_plans


def edit_csv(file: str, edited_file: str, id_zipcode_map):
    """
    Helper function to write zipcode HashMap to the CSV.
    :param file: Name of the original file.
    :param edited_file: Name of the edited file.
    :param id_zipcode_map: Python dictionary of the zipcode HashMap.
    :return: None.
    @author Alan
    """
    with open(file, 'r', encoding='utf-8') as read_obj, \
      open(edited_file, 'w', newline='', encoding='utf-8') as write_obj:
        csv_reader = csv.reader(read_obj, delimiter=',')
        csv_writer = csv.writer(write_obj)
        for row in csv_reader:
            if len(row) == 0 or row[0] == '[idKey]' or row[0] == 'END OF FILE':
                continue
            if int(row[0]) in id_zipcode_map:
                # if the idKey is in i_z_m, we append i_z_m's corresponding value (a list of
                # zipcodes for that idKey) to the row in the csv
                row.append(id_zipcode_map[int(row[0])])
            csv_writer.writerow(row)


def update_run_file(num_new_plans: int):
    """
    File should contain two columns with timestamp and number of unique plans found for each row.
    Updates on each run.
    :param num_new_plans: For second column of the file. New plans found on that run.
    :return: None
    """
    row = f"{utils.get_datetime(datetime_format='%m/%d/%y %H:%M:%S')}, {num_new_plans}"

    if not utils.exists(utils.RUN_HISTORY_FILE):
        with open(utils.RUN_HISTORY_FILE, 'w') as run_file:
            run_file.write(row)
    else:
        with open(utils.RUN_HISTORY_FILE) as contents:
            curr_contents = contents.read()
        with open(utils.RUN_HISTORY_FILE, 'a', newline='') as run_file:
            if len(curr_contents) == 0:
                run_file.write(row)
            else:
                run_file.write("\n" + row)


if __name__ == '__main__':

    # Step 1 - Set up folders.
    setup()

    # Logger set up
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(filename=utils.LOGS_PATH, level=logging.DEBUG,
                        format='%(asctime)s:%(message)s')

    # Step 2 - Download the master CSV and check new plans.
    # Download raw CSV from the Power to Choose website, check whether it has been updated
    # If not, delete it. Delete Spanish rows
    try:
        new_plans = auto_download_csv(utils.CSV_LINK)
        if new_plans is None:
            update_run_file(num_new_plans=0)
            sys.exit("No new plans")
        else:
            update_run_file(num_new_plans=len(new_plans.index))
    except Exception as e:
        error_traceback = traceback.extract_tb(e.__traceback__)
        send_email(
            body=f"Error in Auto Downloading.\nTraceback at {utils.get_datetime()}:\n{error_traceback}",
            files=[utils.LOGS_PATH])

    # Step 3 - Run the code for the differences.
    try:
        # download(csv_filepath=utils.DIFFPLANS_CSV_PATH)
        download(csv_filepath=utils.DIFFPLANS_CSV_PATH, output_fname = "new-plans.csv")
    except Exception as e:
        error_traceback = traceback.extract_tb(e.__traceback__)
        send_email(
            body=f"Error in PDF Downloading.\nTraceback at {utils.get_datetime()}:\n{error_traceback}",
            files=[utils.LOGS_PATH])

    # Also try to download missing PDFs for continued plans
    result = pd.read_csv(utils.RESULT_CSV)
    check_plans = result.loc[result['pdf_filepath'] == 'None']
    check_plans.drop('pdf_filepath', axis=1, inplace=True)
    check_plans.to_csv(utils.CHECKPLANS_CSV_PATH, index=False)
    try:
        download(csv_filepath=utils.CHECKPLANS_CSV_PATH, output_fname = "check-plans.csv")
    except:
        print('Downloading missing PDFs for unchanged plans failed')
        

    # Combine the new-plans.csv and result.csv files
    combine_results()
    
    # Create the JSON with zip code to plan mapping
    map_zips.main()
    
    # Use that mapping to create zip code level CSVs
    map_zips.zipcode_file()
    
    # Stop logging
    logging.shutdown()
