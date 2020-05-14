import sys, os
import pathlib
import pandas as pd

TIMEOUT_LIMIT = 5
CSV_LINK = "http://www.powertochoose.org/en-us/Plan/ExportToCsv"
MASTER_CSV_PATH = "data\\raw.csv"
MASTER_CSV_OLD = "data\\old.csv"
MASTER_CSV_ZIP = "data\\raw_zipcodes.csv"
DATA_DIR = "data\\"
PDF_DIR = "PDFs\\"
LOGS_DIR = "logs\\"
LOGS_PATH = "logs\\download.log"
HTML_KEYWORDS = ["Electricity Price", "Average Monthly Use"]


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

