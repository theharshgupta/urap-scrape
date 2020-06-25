import concurrent.futures
import json
import logging
import os
import traceback
from pathlib import Path

import pandas as pd
from tqdm import tqdm

import texas.pdf as pdf
import texas.utils as utils
from email_service import send_email

dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(Path(dir_path).parent)

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


def download_concurrent(csv_filepath):
    df = pd.read_csv(csv_filepath)
    data_dict = df.to_dict('records')
    plans = []
    result = []

    for d in tqdm(data_dict, desc="PDF Downloading", disable=True):
        plan = Plan(d)
        plans.append(plan)

    with concurrent.futures.ProcessPoolExecutor(max_workers=3) as executor:
        for plan_obj, pdf_filepath in zip(plans, executor.map(pdf.download_pdf_concurrent, plans)):
            if pdf_filepath:
                setattr(plan_obj, "pdf_filepath", pdf_filepath)
                # d['pdf_filepath'] = pdf_filepath
            else:
                setattr(plan_obj, "pdf_filepath", "None")
                # d['pdf_filepath'] = "None"

            d = json.dumps(plan_obj.__dict__)
            result.append(d)

    df = pd.DataFrame(result)
    df.to_csv(os.path.join(utils.RESULT_DIR, "new-plans.csv"), index=False)
    print(df.to_string())


if __name__ == '__main__':
    download_concurrent(csv_filepath=utils.DIFFPLANS_CSV_PATH)
    # try:
    #     # download(csv_filepath=utils.DIFFPLANS_CSV_PATH)
    #     download_concurrent(csv_filepath=utils.DIFFPLANS_CSV_PATH)
    # except Exception as e:
    #     error_traceback = traceback.extract_tb(e.__traceback__)
    #     send_email(
    #         body=f"Error in PDF Downloading.\nTraceback at {utils.get_datetime()}:\n{error_traceback}",
    #         files=[utils.LOGS_PATH])
    #
    # # map_zips.main()
    # logging.shutdown()
