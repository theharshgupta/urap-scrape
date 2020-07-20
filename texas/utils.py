import sys, os
import pathlib
import pandas as pd
from datetime import datetime
import shutil
import pytz
import pickle
import io
from pathlib import Path

dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(Path(dir_path).parent)
sys.path.append(os.getcwd())
sys.path.append(dir_path)

from email_service_TX import send_email
import texas.utils as utils

TIMEOUT_LIMIT = 5
CSV_LINK = "http://www.powertochoose.org/en-us/Plan/ExportToCsv"

CWD = os.curdir
LATEST_CSV_PATH = os.path.join("data", "latest.csv")
DIFFPLANS_CSV_PATH = os.path.join("data", "diffPlans.csv")
CHECKPLANS_CSV_PATH = os.path.join("data", "CheckPDFPlans.csv")
DATA_DIR = "data"
PDF_DIR = os.path.join(DATA_DIR, "PDFs")
LOGS_DIR = "logs"
LOGS_PATH = os.path.join(LOGS_DIR, "download-experimental.log")
HTML_KEYWORDS = ["Electricity Price", "Average Monthly Use"]
PLANS_DIR = os.path.join(DATA_DIR, ".plans")
MASTER_DIR = os.path.join(DATA_DIR, "master")

ZIPCODE_FILE = os.path.join(DATA_DIR, ".texas-zipcodes")
VALID_ZIPS = os.path.join(DATA_DIR, ".ptc-valid-zipcodes")
ZIPCODE_MAP = os.path.join(DATA_DIR, "zipcode_plan_map.json")
CSV_DIR = os.path.join(DATA_DIR, "csv_zipcode")

RESULT_DIR = os.path.join(DATA_DIR, "result")
RESULT_CSV = os.path.join(RESULT_DIR, "result.csv")
NEW_PLANS_RESULT_CSV = os.path.join(RESULT_DIR, "new-plans.csv")
CHECK_PLANS_RESULT_CSV = os.path.join(RESULT_DIR, "check-plans.csv")

RUN_HISTORY_FILE = os.path.join(CWD, 'run_history.txt')


def save_pickle(obj, file):
    """
    A function to save object to a pickle in the file location
    :param obj: what you want to pickle
    :param file: where you want to pickle
    :return: None
    """
    with open(file, 'ab') as f:
        pickle.dump(obj, f)


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

def add_delimiters(fpath, delimiter=','):

    s_data = ''
    max_num_delimiters = 0

    with open(fpath, 'r') as f:
        for line in f:
            s_data += line
            delimiter_count = line.count(delimiter)
            if delimiter_count > max_num_delimiters:
                max_num_delimiters = delimiter_count

    s_delimiters = delimiter * max_num_delimiters + '\n'

    return io.StringIO(s_delimiters + s_data)

def filter_csv(csv_filepath):
    """
    This removes the Spanish rows from CSV and saves it to the same CSV path.
    :param csv_filepath: File path of the CSV.
    :return: None.
    """
    try:
        df = pd.DataFrame(pd.read_csv(csv_filepath))
    except: # work-around for error on 7/16
        df_erred = pd.DataFrame(pd.read_csv(add_delimiters(csv_filepath)))
        new_header = df_erred.iloc[0] #grab the first row for the header
        df_erred = df_erred[1:] #take the data less the header row
        df_erred.columns = new_header
        df = df_erred.copy()
        error_rows = df_erred.index[(df_erred['[Rating]'] == 'Spanish') | (df_erred['[Rating]'] == 'English')].tolist()
        if len(error_rows) == 0:
            send_email(
            body=f"Trouble parsing the CSV downloaded from Power to Choose",
            files=[utils.LOGS_PATH])
        for i in error_rows:
            df.iloc[i,23:28] = df_erred.iloc[i,24:29]
        df = df[df.columns.dropna()]
    df_english = df[df['[Language]'] == 'English']
    df_english = df_english.drop(["[Language]", "[EnrollURL]", "[EnrollPhone]", "[Website]"], axis=1) #jkl
    df_english.to_csv(csv_filepath, index=False)


def get_datetime(datetime_format='%m%d%y_%H_%M_%S'):
    """
    Function to return current datetime.
    :return: the string of current datetime.
    """
    return datetime.today().astimezone(pytz.timezone('US/Pacific')).strftime(datetime_format)


def copy(curr, dest):
    """
    Copies the file.
    :param curr: Curr location.
    :param dest: New location.
    :return: None.
    """
    shutil.copyfile(src=curr, dst=dest)

