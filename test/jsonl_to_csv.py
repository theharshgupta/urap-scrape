import pandas as pd
import json
import csv

#class Doc:
#    info = {}
#    def __init__(self, info):
#        self.info = info


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

def write_to_csv2(doc, keys):
    try:
        with open("testing2.csv", mode = "w", encoding='utf-8', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(keys)
            for d in doc:
                writer.writerow([d.get(i, "NA") for i in keys])
    except IOError:
        print("I/O error")

def fill_suppliers(records, doc):
    for i in range(len(records)):
        info = {}
        document = records[i]['document']['documentText']['content']
        if 'annotations' in records[i].keys():
            for j in range(len(records[i]['annotations'])):
                try:
                    low =int(records[i]['annotations'][j]['textExtraction']['textSegment']['startOffset'])
                    high = int(records[i]['annotations'][j]['textExtraction']['textSegment']['endOffset'])
                    info[records[i]['annotations'][j]['displayName']] = document[low:high]
                except Exception:
                    1+1
        doc.append(info)

def get_fields(doc):
    fields = set()
    for i in range(len(doc)):
        fields.update(doc[i].keys())
    return fields

def run():
    with open('train1.jsonl', "r", encoding="utf8") as f:
        records = [json.loads(line) for line in f]
    doc = []
    fill_suppliers(records, doc)
    fields = get_fields(doc)
    write_to_csv2(doc, fields)

run()
