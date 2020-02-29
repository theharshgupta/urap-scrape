import csv
import pandas as pd
from datetime import datetime
import json
from texas.api_call import API
from datetime import datetime


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

    df2 = pd.DataFrame(pd.read_csv(filepath))
    data_dict2 = df2.to_dict('records')
    for d in data_dict2:
        p = Plan(d)


def map_zipcode():
    """
    This function will be mapping zipcodes to ids or some other identifier
    for each of the plans in the input CSV
    :return: None
    """
    zipcodes = [75001, 75002, 71230]
    id_zipcode_map = API(zipcodes).id_zipcode_map
    return id_zipcode_map


if __name__ == '__main__':
    # parse_csv("master_data.csv")
    map_zipcode()
