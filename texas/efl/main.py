from google.cloud import storage
import pdfplumber as plum
from string import Template

BUCKET_NAME = "zckharsh"



def pdfplumber_extraction(filepath):
    pdf = plum.open(filepath)
    first_page = pdf.pages[0]
    tables = first_page.find_tables()
    text = first_page.extract_text()
    if "cargos" in text:
        pass
    else:
        print(text.encode("utf-8").decode("utf-8"))
        # for table in tables:
        #     print(table.extract())

def auto_ml():
    """
    Using Google's AutoML NLP and Entity extraction tool
    :return:
    """
    pass


def create_jsonl():
    import json
    import jsonlines
    object = json.load(open("test2.json"))
    print(object)
    items = {"document": {"input_config": {"gcs_source": {"input_uris": ["gs://pdf_bucket_urap/1880.pdf"]}}}}
    with jsonlines.open('test2.jsonl', 'w') as writer:
        writer.write(object)

def classify_pdf():
    """
    Each pdf is classified as a table or paragraph pdf
    :return: None
    """

    import pathlib
    templ = Template("PDF file: $filepath")

    PDF_FOLDER = pathlib.Path("/Users/harsh/Desktop/coding/urap-scrape/texas/PDFs/")
    for file in pathlib.Path.iterdir(PDF_FOLDER):
        print(templ.substitute(filepath=str(file.absolute())))
        pdfplumber_extraction(filepath=file.absolute())



def create_bucket():
    """Creates a new bucket."""
    source_file_name = "test2.jsonl"
    destination_blob_name = source_file_name
    # destination_blob_name = "59.pdf"
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)


if __name__ == '__main__':
    classify_pdf()
