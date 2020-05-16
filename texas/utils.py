import sys, os
import pathlib
import pandas as pd
from datetime import datetime
import shutil
import pytz

TIMEOUT_LIMIT = 5
CSV_LINK = "http://www.powertochoose.org/en-us/Plan/ExportToCsv"
LATEST_CSV_PATH = os.path.join("data", "latest.csv")
MASTER_CSV_ZIP = os.path.join("data", "raw_zipcodes.csv")
DATA_DIR = "data"
PDF_DIR = "PDFs"
LOGS_DIR = "logs"
LOGS_PATH = os.path.join(LOGS_DIR, "download.log")
HTML_KEYWORDS = ["Electricity Price", "Average Monthly Use"]
PLANS_DIR = os.path.join(DATA_DIR, ".plans")
MASTER_DIR = os.path.join(DATA_DIR, "master")


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


def filter_spanish_rows(csv_filepath):
    """
    This removes the Spanish rows from CSV and saves it to the same CSV path.
    :param csv_filepath: File path of the CSV.
    :return: None.
    """
    df = pd.DataFrame(pd.read_csv(csv_filepath))
    df_english = df[df['[Language]'] == 'English']
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
    shutil.copy(src=curr, dst=dest)


