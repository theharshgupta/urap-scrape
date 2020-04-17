from google.cloud import storage
import pdfplumber as plum
from string import Template
import pathlib
import pandas as pd
import os

BUCKET_NAME = "zckharsh"
PDF_FOLDER = pathlib.Path("/Users/harsh/Desktop/coding/urap-scrape/texas/PDFs/")


def pdf_to_text(filepath):
    """
    Uses pdfplumber library to convert PDF to string.
    Ignores Spanish PDFs
    :param filepath: filepath for the PDF
    :return: text content
    """
    pdf = plum.open(filepath)
    text_content = ""
    for page in pdf.pages:
        text_content = text_content + "\n\n" + page.extract_text()
    if "cargos" in text_content:
        pass
    else:
        return text_content.encode("utf-8").decode("utf-8")


def create_jsonl():
    import json
    import jsonlines
    object = json.load(open("test2.json"))
    print(object)
    items = {"document": {"input_config": {
        "gcs_source": {"input_uris": ["gs://pdf_bucket_urap/1880.pdf"]}}}}
    with jsonlines.open('test2.jsonl', 'w') as writer:
        writer.write(object)


def dataset():
    """
    We will use this function to create the Dataset for AutoML Google
    Pipeline: PDF -> Text -> CSV -> JSONL
    :return: None (saves the file to CSV)
    """
    json_result = {}
    annotations = []
    sample_line = {"annotations": [{"text_extraction": {"text_segment": {"end_offset": 54, "start_offset": 27}}, "display_name": "SpecificDisease"},
                                   {"text_extraction": {"text_segment": {"end_offset": 173, "start_offset": 156}}, "display_name": "SpecificDisease"},
                                   {"text_extraction": {"text_segment": {"end_offset": 179, "start_offset": 176}}, "display_name": "SpecificDisease"},
                                   {"text_extraction": {"text_segment": {"end_offset": 246, "start_offset": 243}}, "display_name": "Modifier"},
                                   {"text_extraction": {"text_segment": {"end_offset": 340, "start_offset": 337}}, "display_name": "Modifier"},
                                   {"text_extraction": {"text_segment": {"end_offset": 698, "start_offset": 695}}, "display_name": "Modifier"}],
                   "text_snippet": {"content": "1301937\tMolecular basis of hexosaminidase A deficiency and pseudodeficiency in the Berks County Pennsylvania Dutch.\tFollowing the birth of two infants with Tay-Sachs disease ( TSD ) , a non-Jewish , Pennsylvania Dutch kindred was screened for TSD carriers using the biochemical assay . A high frequency of individuals who appeared to be TSD heterozygotes was detected ( Kelly et al . , 1975 ) . Clinical and biochemical evidence suggested that the increased carrier frequency was due to at least two altered alleles for the hexosaminidase A alpha-subunit . We now report two mutant alleles in this Pennsylvania Dutch kindred , and one polymorphism . One allele , reported originally in a French TSD patient ( Akli et al . , 1991 ) , is a GT-- > AT transition at the donor splice-site of intron 9 . The second , a C-- > T transition at nucleotide 739 ( Arg247Trp ) , has been shown by Triggs-Raine et al . ( 1992 ) to be a clinically benign \" pseudodeficient \" allele associated with reduced enzyme activity against artificial substrate . Finally , a polymorphism [ G-- > A ( 759 ) ] , which leaves valine at codon 253 unchanged , is described  .\n "}}

    df = pd.read_csv("../master_data_en.csv")

    for file in pathlib.Path.iterdir(PDF_FOLDER):
        plan_id = int(str(file.absolute()).split('/')[-1].strip().split('.')[0])
        text_content = pdf_to_text(file)
        sample_annotation = {"text_extraction": {"text_segment": {"end_offset": 0, "start_offset": 0}}, "display_name": "None"}
        plan_row = df[df['[idKey]'] == plan_id]['[RateType]']
        rate_type = pd.Series(plan_row).array[0]
        pos = text_content.find(rate_type)
        print("Found @" + str(pos))









def classify_pdf():
    """
    Each pdf is classified as a table or paragraph pdf
    :return: None
    """

    templ = Template("PDF file: $filepath")
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
        print(templ.substitute(filepath=str(file.absolute())))
        text_content = pdf_to_text(filepath=file.absolute())
        print(
            f"Found contract term in text: {text_content.find(str(int(plan_row)))}")


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
    dataset()
