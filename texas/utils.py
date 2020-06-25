import sys, os
import pathlib
import pandas as pd
from datetime import datetime
import shutil
import pytz
import pickle

TIMEOUT_LIMIT = 5
CSV_LINK = "http://www.powertochoose.org/en-us/Plan/ExportToCsv"
LATEST_CSV_PATH = os.path.join("data", "latest.csv")
DIFFPLANS_CSV_PATH = os.path.join("data", "diffPlans.csv")
DATA_DIR = "data"
PDF_DIR = os.path.join(DATA_DIR, "PDFs")
LOGS_DIR = "logs"
LOGS_PATH = os.path.join(LOGS_DIR, "download-experimental.log")
HTML_KEYWORDS = ["Electricity Price", "Average Monthly Use"]
PLANS_DIR = os.path.join(DATA_DIR, ".plans")
MASTER_DIR = os.path.join(DATA_DIR, "master")
ZIPCODE_FILE = os.path.join(DATA_DIR, ".zipcodes")
VALID_ZIPS = os.path.join(DATA_DIR, ".valid_zip")
ZIPCODE_MAP = os.path.join(DATA_DIR, "zipcode_plan_map.json")
CSV_DIR = os.path.join(DATA_DIR, "csv_zipcode")
RESULT_DIR = os.path.join(DATA_DIR, "result")


def save_pickle(object, file):
    """
    A function to save object to a pickle in the file location
    :param object: what you want to pickle
    :param file: where you want to pickle
    :return: None
    """
    with open(file, 'ab') as f:
        pickle.dump(object, f)


def get_pickle(file):
    """
    Return the pickle object from the file location
    :param file: the place where the pickle is stored
    :return: the pickled object
    """

    with open(file, 'rb') as f:
        return pickle.load(f)


def block_print():
    """
    Blocks all print statements when called
    :return: None
    """
    sys.stdout = open(os.devnull, 'w')


def enable_print():
    """
    Enable the print statements. Called after block_print function
    :return: None
    """
    sys.stdout = sys.__stdout__


def exists(filepath):
    """
    Checks the filepath and returns if it exists. If it does not, then a file is created at
    that path.
    :param filepath: the exact location to check and create.
    :return: True is exists and False if file is created.
    """
    return pathlib.Path(filepath).exists()


def rename(current, new):
    """
    Renames the file.
    :param current: Old filename.
    :param new: New filename.
    :return: None.
    """
    if not exists(current):
        return
    else:
        pathlib.Path(current).rename(new)


def filter_csv(csv_filepath):
    """
    This removes the Spanish rows from CSV and saves it to the same CSV path.
    :param csv_filepath: File path of the CSV.
    :return: None.
    """
    df = pd.DataFrame(pd.read_csv(csv_filepath))
    df_english = df[df['[Language]'] == 'English']
    df_english = df_english.drop(["[Language]", "[EnrollURL]", "[EnrollPhone]", "[Website]"], axis=1) #jkl
    df_english.to_csv(csv_filepath, index=False)


def get_datetime():
    """
    Function to return current datetime.
    :return: the string of current datetime.
    """
    return datetime.today().astimezone(pytz.timezone('US/Pacific')).strftime('%m%d%y_%H_%M_%S')


def copy(curr, dest):
    """
    Copies the file.
    :param curr: Curr location.
    :param dest: New location.
    :return: None.
    """
    shutil.copyfile(src=curr, dst=dest)

