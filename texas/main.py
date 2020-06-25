import os
from pathlib import Path
import csv
import pickle
import concurrent.futures
import traceback
import pathlib
from email_service import send_email
import pandas as pd
from datetime import datetime
import requests
from requests.exceptions import Timeout
import json
import urllib.request
import logging
import texas.pdf as pdf
import texas.utils as utils
from tqdm import tqdm
from csv_diff import load_csv, compare
import texas.map_zipcodes as map_zips

dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(Path(dir_path).parent)
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

    updated_plans = pd.read_csv(utils.NEW_PLANS_RESULT_CSV)
    updated_plan_ids = updated_plans['id_key'].values
    result = pd.read_csv(utils.RESULT_CSV)
    old = result.loc[~result['id_key'].isin(updated_plan_ids)]
    merged = pd.DataFrame(old).append(updated_plans)
    print(merged.to_string())
    merged.to_csv(utils.RESULT_CSV, index=False)
    print("Find your results at:", utils.RESULT_CSV)


def download(csv_filepath):
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
        pdf_filepath = pdf.download_pdf(pdf_url=plan.facts_url, plan=plan)
        if pdf_filepath:
            d['pdf_filepath'] = pdf_filepath
        else:
            d['pdf_filepath'] = "None"
        result.append(d)
    df = pd.DataFrame(result)
    df.to_csv(os.path.join(utils.RESULT_DIR, "new-plans.csv"), index=False)
    print(df.to_string())


def setup():
    """
    Sets up the folders for all functions to run.
    :return: None.
    """
    print("Running the presetupm to check for folders and create them. ")
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

    print("Pre setup completed. ")


def auto_download_csv(url):
    """
    Download raw CSV from PTC website. The function makes sure that a diffPlans.csv is
    created that contains all the plans that need to be "considered" -- i.e. to be downloaded,
    worked with, mapped, etc.
    :param url: URL to make a request.
    :return: None.
    """
    print("\nRunning Auto Download CSV to download the MASTER CSV...")
    filepath = f"{os.path.join(utils.MASTER_DIR, utils.get_datetime().replace('_', '-'))}.csv"

    urllib.request.urlretrieve(url, filepath)
    utils.filter_csv(csv_filepath=filepath)

    # If latest.csv file does not exist, then rename the file downloaded to latest.csv
    if not utils.exists(utils.LATEST_CSV_PATH):
        utils.copy(filepath, utils.LATEST_CSV_PATH)
        utils.copy(utils.LATEST_CSV_PATH, utils.DIFFPLANS_CSV_PATH)
        return 1
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


if __name__ == '__main__':

    combine_results()
    exit(1)

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
            exit()
    except Exception as e:
        error_traceback = traceback.extract_tb(e.__traceback__)
        send_email(
            body=f"Error in Auto Downloading.\nTraceback at {utils.get_datetime()}:\n{error_traceback}",
            files=[utils.LOGS_PATH])

    # Step 3 - Run the code for the differences.
    try:
        # download(csv_filepath=utils.DIFFPLANS_CSV_PATH)
        download(csv_filepath=utils.DIFFPLANS_CSV_PATH)
    except Exception as e:
        error_traceback = traceback.extract_tb(e.__traceback__)
        send_email(
            body=f"Error in PDF Downloading.\nTraceback at {utils.get_datetime()}:\n{error_traceback}",
            files=[utils.LOGS_PATH])

    # map_zips.main()
    logging.shutdown()
