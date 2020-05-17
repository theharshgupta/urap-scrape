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


def update_valid_zips(valid_zipcodes):
    new_obj = {"date": get_datetime(),
               "data": valid_zipcodes}
    print(new_obj)
    if exists(VALID_ZIPS):
        os.remove(VALID_ZIPS)
    save_pickle(new_obj, VALID_ZIPS)
    print("Valid zip codes file was updated!")


id_zipcode_map = {}


class Zipcode:
    zipcodes = None
    base_url = "http://api.powertochoose.org/api/PowerToChoose/plans?zip_code="
    valid_zips = []

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
        # Each data row has an plan_id that should be same to the idKey in the CSV
        data = json.loads(response.text)['data']
        # print('Zipcode: ' + str(zipcode), "has plan data:", len(data),
        #       "-> Time outs:", timeouts)
        if len(data) > 0:
            df = pd.DataFrame.from_records(data)
            self.valid_zips.append(zipcode)

            if "plan_id" not in df.columns:
                print(df)
            else:
                # id_zipcode_map[str(zipcode)] = df["plan_id"].tolist()
                # print(id_zipcode_map)
                return df["plan_id"].tolist()

            # exit()
            # for row in data:
            #     if row['plan_id'] in self.id_zipcode_map.keys():
            #         self.id_zipcode_map[row['plan_id']] = self.id_zipcode_map[row['plan_id']] \
            #                                               + [zipcode]
            #     else:
            #         self.id_zipcode_map[row['plan_id']] = [zipcode]
            #     print(self.id_zipcode_map)

    def perform(self):
        """
        creates API object for all the zipcodes. The tqdm module is for a progress bar.
        :return: None
        """
        for zipcode in tqdm.tqdm(self.zipcodes, desc="Zipcode Mapping"):
            self.api_data(zipcode)


def check_api_zicodes():
    """
    Pickle checker for API for zipcodes. Gets all the zipcodes
    :return:
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

    return zipcodes


def check_valid_zips():
    update = False
    if exists(VALID_ZIPS):
        old_obj = get_pickle(VALID_ZIPS)
        print(old_obj)
        last_pickle = old_obj["date"]
        if (datetime.now() - datetime.strptime(last_pickle, '%m%d%y_%H_%M_%S')) > timedelta(days=7):
            update = True
        else:
            valid_zipcodes = old_obj["data"]
            return valid_zipcodes

    if not exists(VALID_ZIPS) or update:
        return None


def main():
    """
    This function will be mapping zipcodes to idKey (plan_id in dict)
    So key = idKey, value = list(zipcodes with that plan)
    for each of the plans in the input CSV -
    :return: the mapping
    """
    zipcodes = check_api_zicodes()
    valid_zipcodes = check_valid_zips()
    if valid_zipcodes and len(valid_zipcodes) > 500:
        zipcodes = valid_zipcodes
    zipcodes = sorted([int(x) for x in zipcodes])
    print(len(zipcodes))
    time.sleep(1)
    obj = Zipcode(zipcodes)

    with concurrent.futures.ProcessPoolExecutor(max_workers=10) as executor:
        for zipcode, plans in tqdm.tqdm(zip(zipcodes, executor.map(obj.api_data, zipcodes)), total=len(zipcodes)):
            if plans:
                id_zipcode_map[str(zipcode)] = plans

    print(id_zipcode_map)
    with open(ZIPCODE_MAP, 'w') as f:
        json.dump(id_zipcode_map, f, sort_keys=True, indent=4)
    update_valid_zips(list(id_zipcode_map.keys()))

    # edit_csv('master_data_en.csv', 'master_data_en_zipcodes.csv', id_zipcode_map)
    # edit_csv("data\\05_15_2020_03_59.csv", utils.MASTER_CSV_ZIP, id_zipcode_map)


def zipcode_file():
    """
    Converts raw CSV to zipcode level CSVs
    :return: None
    """
    if not exists(CSV_DIR):
        os.mkdir(CSV_DIR)

    with open(ZIPCODE_MAP, 'r') as f:
        data = json.load(f)

    df = pd.read_csv(LATEST_CSV_PATH)

    for zipcode, plans in tqdm.tqdm(dict(data).items(), total=len(data)):
        filename = f"{zipcode}_{get_datetime()}.csv"
        plans_df = df[df["[idKey]"].isin(plans)]
        plans_df["Zipcode"] = zipcode
        plans_df.to_csv(os.path.join(CSV_DIR, filename), index=False, float_format="%.5f")


if __name__ == '__main__':
    # block_print()
    zipcode_file()
    # test1()
