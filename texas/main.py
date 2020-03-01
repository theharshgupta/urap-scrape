import csv
import pandas as pd
from datetime import datetime
import requests
import json
from scrapeHelper import downloadPDF, getEmbeddedPDFLink


class API:
    zipcodes = None
    url = "http://api.powertochoose.org/api/PowerToChoose/plans?zip_code="
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

        response = requests.get(self.url + str(zipcode), verify=False)
        # Each data row has an plan_id that should be same to the idKey in the CSV
        data = json.loads(response.text)['data']
        for row in data:
            if row['plan_id'] in self.id_zipcode_map.keys():
                self.id_zipcode_map[row['plan_id']] = self.id_zipcode_map[
                                                          row['plan_id']] + [
                                                          zipcode]
            else:
                self.id_zipcode_map[row['plan_id']] = [zipcode]

    def all_zips(self):
        """
        creates API object for all the zipcodes
        :return: None
        """
        for zipcode in self.zipcodes:
            self.api_data(zipcode)


class Plan:
    # Define class variables as per the column names

    supplier_name: int = None
    rate_type: str = None
    fixed_charge: bool = False
    variable_rate: int = None
    introductory_rate: int = None
    introductory_price_value: float = None
    enrollment_fee: float = None
    contract_term: str = "0"
    early_termination_fee: int = 0
    automatic_renewal_type: str = None
    automatic_renewal_detail: str = None
    percent_renewable: int = 0
    renewable_description: str = None
    incentives_special_terms: str = None
    incumbent_flag: bool = False
    estimated_cost: float = 0
    other_product_service: str = None
    # Making the zipcode a string because of preceeding zeros
    zipcode: str = None
    date_downloaded: str = str(datetime.today())
    tdu_service_territory: str = None
    plan_name: str = None
    variable_rate_500: float = 0.0
    variable_rate_1000: float = 0.0
    variable_rate_2000: float = 0.0

    def __init__(self, row_data):
        """
        Constructor for the class for the Plan
        :param row_data: type Python dictionary
        """
        #for some reason this block raises a KeyError when I run download()... I just commented it out for now until theres abetter solution
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

        #(alan) one variable for every single column in the csv
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

def download(filepath):
    #(alan) df2 is a slight variation of the df object above (I think?) We're iterating over each of the plans in df2, using their
    #   FactsURL to download the pdf's (with idKey as the name). This is done with the help of scrapeHelper and pdfReader from
    #   last semester's PTC, which isn't fully robust yet. Note that line 130 of scrapeHelper depends on the location of wkhtmltopdf
    #   and as such may need to be changed from person to person.
    df2 = pd.DataFrame(pd.read_csv(filepath))
    data_dict2 = df2.to_dict('records')
    for d in data_dict2:
        #print(d)
        #print()
        plan = Plan(d)
        downloadPDF(getEmbeddedPDFLink(plan.FactsURL), plan.idKey, "PDFs/")


def map_zipcode():
    """
    This function will be mapping zipcodes to ids or some other identifier
    for each of the plans in the input CSV -
    :return: None
    """
    zipcodes = [75001, 75002, 71230]
    id_zipcode_map = API(zipcodes).id_zipcode_map
    return id_zipcode_map


if __name__ == '__main__':
    #parse_csv("master_data.csv")
    download("master_data.csv")
    map_zipcode()
