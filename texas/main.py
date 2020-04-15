import csv
import pandas as pd
from datetime import datetime
import requests
from requests.exceptions import Timeout
import json
import logging
from texas.pdf import download_pdf
from texas.utils import block_print, enable_print
from tqdm import tqdm


logging.basicConfig(format="%(asctime)s: %(message)s")
# Set timeout limit in seconds


class API:
    zipcodes = None
    base_url = "http://api.powertochoose.org/api/PowerToChoose/plans?zip_code="
    id_zipcode_map = {}

    def __init__(self, zipcodes):
        self.zipcodes = zipcodes
        self.all_zips()

    def api_data(self, zipcode):
        """
        Gets data and parses it as per PowerToChoose module specifications
        :param zipcode: zipcode of the place
        :return: None
        """
        timeouts = []
        try:
            response = requests.get(self.base_url + str(zipcode), verify=False,
                                    timeout=(2, 5))
        except Timeout:
            timeouts.append(zipcode)
            return
        # Each data row has an plan_id that should be same to the idKey in the CSV
        data = json.loads(response.text)['data']
        print('Zipcode: ' + str(zipcode), " has plan data:", len(data) != 0,
              ". Time outs:", timeouts)
        for row in data:
            if row['plan_id'] in self.id_zipcode_map.keys():
                # This appends new zipcodes to the current planID.
                self.id_zipcode_map[row['plan_id']] = self.id_zipcode_map[row['plan_id']] \
                                                      + [zipcode]
            else:
                # Create a new key-value pair of planID and zipcode in the dict.
                self.id_zipcode_map[row['plan_id']] = [zipcode]

    def all_zips(self):
        """
        creates API object for all the zipcodes. The tqdm module is for a progress bar.
        :return: None
        """
        for zipcode in tqdm(self.zipcodes, desc="Zipcode Mapping"):
            self.api_data(zipcode)


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


def download(csv_filepath):
    """
    Alan Comments: df2 is a slight variation of the df object above (I think?) We're iterating
    over each of the plans in df2, using their FactsURL to download the pdfs (with idKey as the
    name)

    :param csv_filepath:
    :return:
    """
    # df2 = pd.DataFrame(pd.read_csv(filepath))
    # df2 = df2[df2['[Language]'] == 'English']
    df2 = pd.read_csv(csv_filepath)
    data_dict2 = df2.to_dict('records')

    for d in tqdm(data_dict2, desc="PDF Downloading"):
        plan = Plan(d)
        logging.info(f"Checking PDF for {plan.id_key} at {plan.facts_url}")
        download_pdf(pdf_url=plan.facts_url, plan=plan)


def map_zipcode():
    """
    This function will be mapping zipcodes to idKey (plan_id in dict)
    So key = idKey, value = list(zipcodes with that plan)
    for each of the plans in the input CSV -
    :return: the mapping
    """
    # API key has 250 lookups per month
    response = requests.get("https://api.zip-codes.com/ZipCodesAPI.svc/1.0/GetAllZipCodes?state"
                            "=TX&country=US&key=BKSM84KBBL8CIIAYIYIP")
    all_zipcodes = response.json()
    print(all_zipcodes)
    id_zipcode_map = API(all_zipcodes).id_zipcode_map
    print(id_zipcode_map)
    edit_csv('master_data_en.csv', 'master_data_en_zipcodes.csv', id_zipcode_map)
    return id_zipcode_map


def edit_csv(file, edited_file, id_zipcode_map):
    with open(file, 'r', encoding='utf-8') as read_obj, \
            open(edited_file, 'w', newline='', encoding='utf-8') as write_obj:
        csv_reader = csv.reader(read_obj, delimiter=',')
        csv_writer = csv.writer(write_obj)
        for row in csv_reader:
            if len(row) == 0 or row[0] == '[idKey]' or row[0] == 'END OF FILE':
                continue
            if int(row[
                       0]) in id_zipcode_map:  # if the idKey is in i_z_m, we append i_z_m's corresponding value (a list of zipcodes for that idKey) to the row in the csv
                row.append(id_zipcode_map[int(row[0])])
            csv_writer.writerow(row)


if __name__ == '__main__':
    # parse_csv("master_data.csv")
    # download(csv_filepath="master_data_en.csv")
    # block_print()
    map_zipcode()
