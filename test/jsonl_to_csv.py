import pandas as pd
import json
import csv
with open('train1.jsonl', "r") as f:
    records = [json.loads(line) for line in f]
pd.DataFrame.from_records(records()).to_csv('testing.csv')


class Doc:
    info = {}

    def __init__(self, info):
        self.info = info


#to be corrected
def write_to_csv(doc):
    try:
        with open("testing.csv", mode = "w") as csv_file:
            csv_columns = [i for i in range(len(doc))]
            writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
            writer.writeheader()
            for i in range(len(doc)):
                for data in doc[i].info:
                    writer.writerow(data)
    except IOError:
        print("I/O error")


def fill_suppliers(records, doc):
    for i in range(len(records)):
        info = {}
        document = records[i]['document']['documentText']['content']
        if 'annotations' in records[i].keys():
            for j in range(len(records[i]['annotations'])):
                try:
                    low =int(records[i]['annotations'][j]['textExtraction']['textSegment']['startOffset']) - 1
                    high = int(records[i]['annotations'][j]['textExtraction']['textSegment']['endOffset'])
                    info[records[i]['annotations'][j]['displayName']] = document[low:high]
                except Exception:
                    1+1
        doc.append(Doc(info))


def run():
    doc = []
    fill_suppliers(records, doc)
    write_to_csv(doc)

