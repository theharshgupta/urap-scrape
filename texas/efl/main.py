from google.cloud import storage
import pdfplumber as plum
from string import Template
import pathlib
import pandas as pd
import os

BUCKET_NAME = "zckharsh"


def pdfplumber_extraction(filepath):
    pdf = plum.open(filepath)
    first_page = pdf.pages[0]
    text = first_page.extract_text()
    if "cargos" in text:
        pass
    else:
        content = text.encode("utf-8").decode("utf-8")
        return content


def create_jsonl():
    import json
    import jsonlines
    object = json.load(open("test2.json"))
    print(object)
    items = {"document": {"input_config": {
        "gcs_source": {"input_uris": ["gs://pdf_bucket_urap/1880.pdf"]}}}}
    with jsonlines.open('test2.jsonl', 'w') as writer:
        writer.write(object)


def classify_pdf():
    """
    Each pdf is classified as a table or paragraph pdf
    :return: None
    """

    templ = Template("PDF file: $filepath")
    PDF_FOLDER = pathlib.Path(
        "/Users/harsh/Desktop/coding/urap-scrape/texas/PDFs/")
    df = pd.read_csv("../master_data_en.csv")
    plan_ids = list(df["[idKey]"])
    for file in pathlib.Path.iterdir(PDF_FOLDER):
        plan_id = int(str(file.absolute()).split('/')[-1].strip().split('.')[0])
        try:
            if plan_id not in plan_ids:
                print("Triggered to remove file. Aborted.")
                # os.remove(str(file.absolute()))
        except Exception:
            pass
        plan_row = df[df['[idKey]'] == plan_id]['[Renewable]']
        print(str(int(plan_row)))
        print(templ.substitute(filepath=str(file.absolute())))
        text_content = pdfplumber_extraction(filepath=file.absolute())
        print(f"Found contract term in text: {text_content.find(str(int(plan_row)))}")


def create_bucket():
    """Creates a new bucket."""
    for file in os.listdir("../PDFs"):
        source_file_name = f"../PDFs/{file}"
        destination_blob_name = f"PDF/{file}"
        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_name)
        print(f"Uploaded at {destination_blob_name}")


if __name__ == '__main__':
    classify_pdf()
