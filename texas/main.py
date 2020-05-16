import csv
import os
import pathlib
import pickle
import traceback
from email_service import send_email
import pandas as pd
from datetime import datetime
import requests
from requests.exceptions import Timeout
import json
import urllib.request
import logging
import texas.pdf
import texas.utils as utils
from tqdm import tqdm
from csv_diff import load_csv, compare

logging.basicConfig(format="%(asctime)s: %(message)s")

dataset_planids = [12820, 16606, 12822, 16612, 16761, 16690, 16769, 18359, 18361, 16759, 16765,
                   18423, 18419, 18421, 12406, 12411, 18462, 18465, 18463, 18464, 17620, 17621,
                   16146, 16141, 17622, 22032, 22034, 22029, 22039, 18735, 18736, 11561, 11547,
                   11502, 11512, 11513, 11535, 11536, 11528, 20854, 20864, 20866, 20859, 20861,
                   20846, 20848, 4152, 1883, 1986, 1879, 1820, 2859, 1821, 1987, 22845, 22120,
                   22290, 22419, 22210, 21834, 22413, 22647, 5506, 22624, 6165, 6168, 5503, 6163,
                   5886, 355, 456, 59, 132, 16822, 16826, 11119, 11115, 16823, 16821, 11118, 4125,
                   142, 250, 2023, 1874, 2027, 66, 4118, 21197, 22172, 9628, 16466, 16442, 16426,
                   16469, 22772, 17319, 17317, 22771, 20509, 20516, 20515, 20505, 18540, 16539,
                   16531, 16509, 16523, 22783, 22451, 21694, 22454, 22455, 21496, 18374, 17577,
                   18370, 11681, 18373, 18367, 21855, 21857, 20724, 22397, 20090, 22719, 22708,
                   22721, 22703, 22712, 21869, 21792, 21636, 21520, 21790, 20474, 20472, 19452,
                   21934, 20215, 20200, 20738, 20744, 20743, 20735, 21211, 21213, 22221, 22732,
                   22243, 22512, 22261, 22254, 22730, 22744, 22258, 19845, 22689, 22687, 21371,
                   21124, 19025, 21370, 21486, 22544, 22547, 22013, 22012, 22018, 21921, 21329,
                   12060, 18860, 21016, 18779, 18786, 18774, 18772, 12292, 22674, 22909, 17279,
                   17301, 18521, 18537, 18536, 18520, 20789, 20805, 20793, 20798, 20788, 13322,
                   13333, 619, 620, 20850, 20867, 22445, 22443, 20178, 20408, 20373, 21944, 21943,
                   21931, 20670, 20668, 20673, 20655, 20678, 20664, 16771, 20929, 20927, 20935,
                   20904, 20944, 20920, 19787, 22890, 21629, 20959, 22841, 22237, 22364, 22825,
                   15958, 12885, 13014, 13017, 13021, 22411, 22429, 22431, 22762, 17257, 17255,
                   22761, 22602, 22575, 22594, 22586, 22607, 13151, 13141, 13140, 13150, 3200, 3199,
                   11372, 3119, 3061, 18982, 18954, 246, 18981, 21147, 19872, 21344, 20022, 18865,
                   12431, 17234, 18632, 22167, 22518, 22748, 15963, 12973, 12965, 15954]


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

    def equals(self, plan2):
        """
        Compare two plans.
        :param plan2: The other plan.
        :return: True or false.
        """
        if self.id_key == plan2.id_key:
            return True


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

    for d in tqdm(data_dict, desc="PDF Downloading", disable=True):
        plan = Plan(d)
        if "PULSE" in plan.rep_company:
            logging.info(f"Checking PDF for {plan.id_key} at {plan.facts_url}")
            pdf.download_pdf(pdf_url=plan.facts_url, plan=plan)


def setup():
    """
    Sets up the folders for all functions to run.
    :return: None.
    """
    if not utils.exists(utils.PDF_DIR):
        os.mkdir(utils.PDF_DIR)
    if not utils.exists(utils.DATA_DIR):
        os.mkdir(utils.DATA_DIR)
    if not utils.exists(utils.LOGS_DIR):
        os.mkdir(utils.LOGS_DIR)
    if not utils.exists(utils.PLANS_DIR):
        os.mkdir(utils.PLANS_DIR)
    if not utils.exists(utils.MASTER_DIR):
        os.mkdir(utils.MASTER_DIR)


def auto_download_csv(url):
    """
    Download raw CSV from PTC website.
    :param url: URL to make a request.
    :param filepath: file path to save the CSV.
    :return: None.
    """

    dateStr = str(datetime.now().strftime("%m_%d_%Y_%H_%M"))
    filepath = "./data/" + dateStr + ".csv"
    urllib.request.urlretrieve(url, filepath)
    utils.filter_spanish_rows(csv_filepath=filepath)


def diff_check():
    """
    Checks for differences between the last downloaded CSV and the newly
    downloaded one, deleting the new one if there are no differences.
    """
    files = sorted([x for x in os.listdir("./data/") if x.endswith(".csv")], key=lambda x: os.path.getmtime("./data/" + x), reverse=True)
    if len(files) < 2:
        # email_error.send_email("not enough files to compare")
        return
    now = files[0]
    recent = files[1]
    diff = compare(load_csv(open("./data/" + now)), load_csv(open("./data/" + recent)))
    same = True
    for i in range(len(diff['added'])):
        for key in diff['added'][i].keys():
            if diff['added'][i][key] != diff['removed'][i][key]:
                same = False
                break
    if same:
        os.remove("./data/" + now)
        print('deleted')


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
    id_zipcode_map = API(all_zipcodes).id_zipcode_map
    print(id_zipcode_map)
    # edit_csv('master_data_en.csv', 'master_data_en_zipcodes.csv', id_zipcode_map)
    edit_csv(utils.LATEST_CSV_PATH, utils.MASTER_CSV_ZIP, id_zipcode_map)
    return id_zipcode_map


def edit_csv(file: str, edited_file: str, id_zipcode_map):
    """
    Helper function to write zipcode HashMap to the CSV.
    :param file: Name of the original file.
    :param edited_file: Name of the edited file.
    :param id_zipcode_map: Python dictionary of the zipcode HashMap.
    :return: None.
    :@author: Alan
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
    # parse_csv("master_data.csv")
    # Step 0 - Set up folders.
    setup()

    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(filename=utils.LOGS_PATH, level=logging.DEBUG,
                        format='%(asctime)s:%(message)s')
    # Step 1 - Download the CSV
    try:
        auto_download_csv(utils.CSV_LINK)
    except Exception as e:
        error_traceback = traceback.extract_tb(e.__traceback__)
        send_email(body=f"Error in Auto Downloading.\nTraceback at {utils.get_datetime()}:\n{error_traceback}",
                   files=[utils.LOGS_PATH])


    diff_check()

    # Step 3 - Run the code for the differences.
    try:
        download(csv_filepath=utils.LATEST_CSV_PATH)
    except Exception as e:
        error_traceback = traceback.extract_tb(e.__traceback__)
        send_email(body=f"Error in PDF Downloading.\nTraceback at {utils.get_datetime()}:\n{error_traceback}",
                   files=[utils.LOGS_PATH])

    # block_print()
    # map_zipcode()
