import csv
import pandas as pd


def parse_csv(filepath):
    """
    Parsing the exported csv from PowerToChoose website
    :param filepath: the location of the CSV file to parse
    :return: void
    """

    df = pd.read_csv(filepath)
    print(df)



if __name__ == '__main__':
    parse_csv("master_data.csv")

