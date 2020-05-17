import time
import multiprocessing
import concurrent.futures
from socket import timeout
from multiprocessing import Pool
import requests
import tqdm
import pickle
from requests.exceptions import Timeout
from texas.utils import *
import json
from datetime import datetime, timedelta


class Zipcode:
    zipcodes = None
    base_url = "http://api.powertochoose.org/api/PowerToChoose/plans?zip_code="
    id_zipcode_map = {}

    def __init__(self, zipcodes):
        self.zipcodes = zipcodes
        # self.perform()

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
        except Timeout or timeout:
            timeouts.append(zipcode)
            return
        # Each data row has an plan_id that should be same to the idKey in the CSV
        data = json.loads(response.text)['data']
        print('Zipcode: ' + str(zipcode), "has plan data:", len(data),
              "-> Time outs:", timeouts)
        for row in data:
            if row['plan_id'] in self.id_zipcode_map.keys():
                # This appends new zipcodes to the current planID.
                self.id_zipcode_map[row['plan_id']] = self.id_zipcode_map[row['plan_id']] \
                                                      + [zipcode]
            else:
                # Create a new key-value pair of planID and zipcode in the dict.
                self.id_zipcode_map[row['plan_id']] = [zipcode]

    def perform(self):
        """
        creates API object for all the zipcodes. The tqdm module is for a progress bar.
        :return: None
        """
        for zipcode in tqdm.tqdm(self.zipcodes, desc="Zipcode Mapping", disable=True):
            self.api_data(zipcode)


def main():
    """
    This function will be mapping zipcodes to idKey (plan_id in dict)
    So key = idKey, value = list(zipcodes with that plan)
    for each of the plans in the input CSV -
    :return: the mapping
    """
    update = False
    if exists(ZIPCODE_FILE):
        old_obj = get_pickle(ZIPCODE_FILE)
        last_pickle = old_obj["date"]
        if (datetime.now() - datetime.strptime(last_pickle, '%m%d%y_%H_%M_%S')) > timedelta(days=5):
            update = True
        else:
            zipcodes = old_obj["data"]
    if update or not exists(ZIPCODE_FILE):
        response = requests.get("https://api.zip-codes.com/ZipCodesAPI.svc/1.0/GetAllZipCodes?state"
                            "=TX&country=US&key=BKSM84KBBL8CIIAYIYIP")
        zipcodes = response.json()
        new_obj = {"date": get_datetime(),
                   "data": zipcodes}
        save_pickle(new_obj, ZIPCODE_FILE)
        print("Zipcode list updated!")

    obj = Zipcode(zipcodes)
    with concurrent.futures.ProcessPoolExecutor(max_workers=10) as executor:
        for x, y in zip(zipcodes, executor.map(obj.api_data, zipcodes)):
            print(x, y)
    print(obj)
    print(obj.id_zipcode_map)

    # API key has 250 lookups per month

    id_zipcode_map = Zipcode(zipcodes).id_zipcode_map
    # edit_csv('master_data_en.csv', 'master_data_en_zipcodes.csv', id_zipcode_map)
    # edit_csv("data\\05_15_2020_03_59.csv", utils.MASTER_CSV_ZIP, id_zipcode_map)


def test1():
    post_data_1 = dict(parameters=dict(method="plans/count",
                                       plan_type=1,
                                       zip_code="75001",
                                       include_details=False,
                                       language=0))
    # r = requests.post(
    #     "http://powertochoose.com/en-us/service/v1/",
    #     data={"method":"plans","plan_type":1,"zip_code":"75001","include_details":True,"language":0})

    r = requests.post(
        "http://powertochoose.com/en-us/service/v1/",
        data={"method": "TduCompaniesByZip", "zip_code": "75001", "include_details": False, "language": 0})

    print(r.json())


if __name__ == '__main__':
    main()
    # test1()









