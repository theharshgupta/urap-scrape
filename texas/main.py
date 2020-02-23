import csv
import pandas as pd


class Plan:
    # Define the getter and setter methods
    # Define class variables as per the column names

    def __init__(self, row_data):
        """
        Constructor
        :param row_data: Python dictionary
        """
        # You parse the row data
        pass


def parse_csv(filepath):
    """
    Parsing the exported csv from PowerToChoose website
    :param filepath: the location of the CSV file to parse
    :return: void
    """

    df = pd.read_csv(filepath)
    data_dict = pd.DataFrame(df).to_dict()
    print(data_dict)

if __name__ == '__main__':
    parse_csv("master_data.csv")
