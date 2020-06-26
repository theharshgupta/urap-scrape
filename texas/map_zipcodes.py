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
            response = requests.get(self.base_url + str(zipcode), verify=False, timeout=(2, 5))
        except Exception as e:
            timeouts.append(zipcode)
            return None

        data = json.loads(response.text)['data']
        if len(data) > 0:
            df = pd.DataFrame.from_records(data)
            self.valid_zips.append(zipcode)
            if "plan_id" not in df.columns:
                print(df)
                return None
            else:
                # print(df["plan_id"].tolist())
                return df["plan_id"].tolist()

    def perform(self):
        """
        creates API object for all the zipcodes. The tqdm module is for a progress bar.
        :return: None
        """
        for zipcode in tqdm.tqdm(self.zipcodes, desc="Zipcode Mapping"):
            self.api_data(zipcode)


def check_api_zicodes():
    """
    This makes a call to the API which gets TEXAS zipcodes. Currently, if the last API call
    was made more than 5 days ago, a new call is made. Otherwise, old API results are used. This
    is to prevent uneccesary API calls that increases run time. Using pickle.
    :return:
    """
    update = False
    print("Checking for TEXAS Zipcode list locally ...")
    if exists(ZIPCODE_FILE):
        old_obj = get_pickle(ZIPCODE_FILE)
        last_pickle = old_obj["date"]
        if (datetime.now() - datetime.strptime(last_pickle, '%m%d%y_%H_%M_%S')) > timedelta(days=5):
            update = True
        else:
            zipcodes = old_obj["data"]
    if update or not exists(ZIPCODE_FILE):
        print("\tNeeds update or list not found, fetching from the API.")
        response = requests.get("https://api.zip-codes.com/ZipCodesAPI.svc/1.0/GetAllZipCodes?state"
                                "=TX&country=US&key=BKSM84KBBL8CIIAYIYIP")
        zipcodes = response.json()
        new_obj = {"date": get_datetime(),
                   "data": zipcodes}
        if exists(ZIPCODE_FILE):
            os.remove(ZIPCODE_FILE)
        save_pickle(new_obj, ZIPCODE_FILE)
        print("\tZipcode list updated!")
    else:
        print("\tLast fetch within 5 days, returning results from local file.")

    return zipcodes


def check_valid_zips():
    """
    Checks the last saved object of the valid zipcodes for Power To Choose website. This is
    basically a list of all zipcodes in PowerToChoose that have some sort of data. Zipcodes
    that return a 404 or empty data are excluded from the list.
    :return:  PTC valid zipcodes or None.
    """
    print("\nChecking for PowerToChoose valid zipcode list locally ...")
    update = False
    if exists(VALID_ZIPS):
        old_obj = get_pickle(VALID_ZIPS)
        last_pickle = old_obj["date"]
        if (datetime.now() - datetime.strptime(last_pickle, '%m%d%y_%H_%M_%S')) > timedelta(days=7):
            update = True
        else:
            valid_zipcodes = old_obj["data"]
            print("\tList found, returning data.")
            return valid_zipcodes

    if not exists(VALID_ZIPS) or update:
        print("\tList is either NOT found, or needs to be updated.")
        return None


def main():
    """
    This function will be mapping zipcodes to idKey (plan_id in dict)
    So key = idKey, value = list(zipcodes with that plan)
    for each of the plans in the input CSV -
    :return: the mapping is saved to ZIPCODE_MAP
    """
    zipcodes = check_api_zicodes()
    valid_zipcodes = check_valid_zips()
    if valid_zipcodes and len(valid_zipcodes) > 500:
        zipcodes = valid_zipcodes
    zipcodes = sorted([int(x) for x in zipcodes])
    obj = Zipcode(zipcodes)

    with concurrent.futures.ProcessPoolExecutor(max_workers=10) as executor:
        for zipcode, plans in tqdm.tqdm(zip(zipcodes, executor.map(obj.api_data, zipcodes)), total=len(zipcodes), desc="Zipcode Mapping"):
            if plans and len(plans) > 0:
                id_zipcode_map[str(zipcode)] = plans

    print(id_zipcode_map)
    with open(ZIPCODE_MAP, 'w') as f:
        json.dump(id_zipcode_map, f, sort_keys=True, indent=4)

    update_valid_zips(list(id_zipcode_map.keys()))


def zipcode_file():
    """
    Converts raw CSV to zipcode level CSVs
    :return: None
    """
    if not exists(CSV_DIR):
        os.mkdir(CSV_DIR)

    # We want to create a new folder with the new iterations.
    timestamp_dir = os.path.join(CSV_DIR, get_datetime().replace("_", "-"))
    os.mkdir(timestamp_dir)
    with open(ZIPCODE_MAP, 'r') as f:
        data = json.load(f)

    df = pd.read_csv(RESULT_CSV)

    for zipcode, plans in tqdm.tqdm(dict(data).items(), total=len(data)):
        filepath = os.path.join(timestamp_dir, f"{zipcode}_{get_datetime()}.csv")
        plans_df = df[df["id_key"].isin(plans)]
        plans_df["Zipcode"] = zipcode
        plans_df.to_csv(filepath, index=False)
        # print("Saving", filepath)


if __name__ == '__main__':
    # block_print()
    # Step 1 - Create the JSON with zip code to plan mapping.
    main()
    # Step 2 - Use that mapping to create zip code level CSVs.
    # zipcode_file()
