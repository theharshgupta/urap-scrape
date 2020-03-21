import csv
import pandas as pd
from datetime import datetime
import requests
from requests.exceptions import Timeout
import json
from texas.pdf import download_pdf
from texas.utils import block_print, enable_print
# from pdf import download_pdf
from tqdm import tqdm


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
        print('_' + str(zipcode), " has plan data:", len(data) != 0,
              " timemouts:", timeouts)
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
        """
        if isinstance(row_data, dict):
            self.supplier_name = row_data['[RepCompany]']
            self.plan_name = row_data['[Product]']
            self.rate_type = row_data['RateType']
            self.fixed_charge = row_data['supplier_name']
            self.variable_rate = row_data['supplier_name']
            self.introductory_rate = row_data['introductory_rate']
            self.introductory_price_value = row_data['introductory_price_value']
            self.enrollment_fee = row_data['enrollment_fee']
            self.contract_term = row_data['contract_term']
            self.early_termination_fee = row_data['early_termination_fee']
            self.automatic_renewal_type = row_data['automatic_renewal_type']
            self.automatic_renewal_detail = row_data['automatic_renewal_detail']
            self.percent_renewable = row_data['percent_renewable']
            self.renewable_description = row_data['renewable_description']
            self.incentives_special_terms = row_data['incentives_special_terms']
            self.incumbent_flag = row_data['incumbent_flag']
            self.estimated_cost = row_data['estimated_cost']
            self.other_product_service = row_data['other_product_service']
            self.zipcode = row_data['zipcode']
            self.tdu_service_territory = row_data['[TduCompanyName]']
            self.variable_rate_500 = row_data['[kwh500]']
            self.variable_rate_1000 = row_data['[kwh1000]']
            self.variable_rate_2000 = row_data['[kwh2000]']
        """
        self.idKey = row_data.get("[idKey]")
        self.TduCompanyName = row_data.get("[TduCompanyName]")
        self.RepCompany = row_data.get("[RepCompany]")
        self.Product = row_data.get("[Product]")
        self.kwh500 = row_data.get("[kwh500]")
        self.kwh1000 = row_data.get("[kwh1000]")
        self.kwh2000 = row_data.get("[kwh2000]")
        self.Fees_Credits = row_data.get("[Fees/Credits]")
        self.PrePaid = row_data.get("[PrePaid]")
        self.TimeOfUse = row_data.get("[TimeOfUse]")
        self.Fixed = row_data.get("[Fixed]")
        self.RateType = row_data.get("[RateType]")
        self.Renewable = row_data.get("[Renewable]")
        self.TermValue = row_data.get("[TermValue]")
        self.CancelFee = row_data.get("[CancelFee]")
        self.Website = row_data.get("[Website]")
        self.SpecialTerms = row_data.get("[SpecialTerms]")
        self.TermsURL = row_data.get("[TermsURL]")
        self.Promotion = row_data.get("[Promotion]")
        self.PromotionDesc = row_data.get("[PromotionDesc]")
        self.FactsURL = row_data.get("[FactsURL]")
        self.EnrollURL = row_data.get("[EnrollURL]")
        self.PrepaidURL = row_data.get("[PrepaidURL]")
        self.EnrollPhone = row_data.get("[EnrollPhone]")
        self.NewCustomer = row_data.get("[NewCustomer]")
        self.MinUsageFeesCredits = row_data.get("[MinUsageFeesCredits]")
        self.Language = row_data.get("[Language]")
        self.Rating = row_data.get("[Rating]")
        self.zipcodes = []


def parse_csv(filepath):
    """
    Parsing the exported csv from PowerToChoose website
    :param filepath: the location of the CSV file to parse
    :return: void
    """
    df = pd.read_csv(filepath)
    headers = df.columns
    data_dict = json.loads(
        pd.DataFrame(df).reset_index().to_json(orient='records'))

    for d in data_dict:
        print(d)
        print()


def download(filepath):
    """
    Alan Comments: df2 is a slight variation of the df object above (I think?) We're iterating
    over each of the plans in df2, using their FactsURL to download the pdfs (with idKey as the
    name)

    :param filepath:
    :return:
    """
    df2 = pd.DataFrame(pd.read_csv(filepath))
    df2 = df2[df2['[Language]'] == 'English']
    df2.to_csv("master_data_en.csv", index=False)
    data_dict2 = df2.to_dict('records')

    for d in tqdm(data_dict2, desc="PDF Downloading"):
        plan = Plan(d)
        block_print()
        download_pdf(pdf_url=plan.FactsURL, plan=plan)


def map_zipcode():
    """
    This function will be mapping zipcodes to idKey (plan_id in dict)
    So key = idKey, value = list(zipcodes with that plan)
    for each of the plans in the input CSV -
    :return: the mapping
    """
    # api key has 250 lookups per month
    response = requests.get("https://api.zip-codes.com/ZipCodesAPI.svc/1.0/GetAllZipCodes?state"
                            "=TX&country=US&key=BKSM84KBBL8CIIAYIYIP")
    all_zipcodes = response.json()
    print(all_zipcodes)
    id_zipcode_map = API(all_zipcodes).id_zipcode_map
    print(id_zipcode_map)
    edit_csv('master_data.csv', 'master_data_withZipcodes.csv', id_zipcode_map)
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
    # download("master_data.csv")
    block_print()
    map_zipcode()
    # parse_csv("master_data_withZipcodes.csv")
