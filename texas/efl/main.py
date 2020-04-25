from google.cloud import storage
import pdfplumber as plum
from string import Template
from pathlib import Path
import shutil
import numpy as np
import pathlib
import pandas as pd
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)

BUCKET_NAME = "zckharsh"
PDF_FOLDER = pathlib.Path("/Users/harsh/Desktop/coding/urap-scrape/texas/PDFs/")
dataset_planids = [12820, 16606, 12822, 16612, 16761, 16690, 16769, 18359, 18361, 16759, 16765,
                   18423, 18419, 18421, 12406, 12411, 18462, 18465, 18463, 18464, 17620, 17621,
                   16146, 16141, 17622, 22032, 22034, 22029, 22039, 18735, 18736, 11561, 11547,
                   11502, 11512, 11513, 11535, 11536, 11528, 20854, 20864, 20866, 20859, 20861,
                   20846, 20848, 4152, 1883, 1986, 1879, 1820, 2859, 1821, 1987, 22845, 22120,
                   22290, 22419, 22210, 21834, 22413, 22647, 5506, 22624, 6165, 6168, 5503, 6163,
                   5886, 355, 456, 59, 132, 16822, 16826, 11119, 11115, 16823, 16821, 11118, 4125,
                   142, 250, 2023, 1874, 2027, 66, 4118, 21197, 22172, 9628, 16466, 16442, 16426,
                   16469, 22772, 17319, 17317, 22771, 20509, 20516, 20515, 20505, 18540, 16539,
                   16531, 16509, 16523, 22783, 22451, 21694, 22454, 22455, 21496, 18374, 17577,
                   18370, 11681, 18373, 18367, 21855, 21857, 20724, 22397, 20090, 22719, 22708,
                   22721, 22703, 22712, 21869, 21792, 21636, 21520, 21790, 20474, 20472, 19452,
                   21934, 20215, 20200, 20738, 20744, 20743, 20735, 21211, 21213, 22221, 22732,
                   22243, 22512, 22261, 22254, 22730, 22744, 22258, 19845, 22689, 22687, 21371,
                   21124, 19025, 21370, 21486, 22544, 22547, 22013, 22012, 22018, 21921, 21329,
                   12060, 18860, 21016, 18779, 18786, 18774, 18772, 12292, 22674, 22909, 17279,
                   17301, 18521, 18537, 18536, 18520, 20789, 20805, 20793, 20798, 20788, 13322,
                   13333, 619, 620, 20850, 20867, 22445, 22443, 20178, 20408, 20373, 21944, 21943,
                   21931, 20670, 20668, 20673, 20655, 20678, 20664, 16771, 20929, 20927, 20935,
                   20904, 20944, 20920, 19787, 22890, 21629, 20959, 22841, 22237, 22364, 22825,
                   15958, 12885, 13014, 13017, 13021, 22411, 22429, 22431, 22762, 17257, 17255,
                   22761, 22602, 22575, 22594, 22586, 22607, 13151, 13141, 13140, 13150, 3200, 3199,
                   11372, 3119, 3061, 18982, 18954, 246, 18981, 21147, 19872, 21344, 20022, 18865,
                   12431, 17234, 18632, 22167, 22518, 22748, 15963, 12973, 12965, 15954]


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

    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)

    with jsonlines.open('label_data.jsonl', 'w') as writer:
        for blob in bucket.list_blobs():
            if "PDF" in blob.name:
                uri = "gs://zckharsh/" + blob.name
                items = {"document": {"input_config": {
                    "gcs_source": {"input_uris": [uri]}}}}
                writer.write(items)


def dataset():
    """
    We will use this function to create the Dataset for AutoML Google
    Pipeline: PDF -> Text -> CSV -> JSONL
    :return: None (saves the file to CSV)
    """
    json_result = {}
    annotations = []
    sample_line = {"annotations": [
        {"text_extraction": {"text_segment": {"end_offset": 54, "start_offset": 27}},
         "display_name": "SpecificDisease"},
        {"text_extraction": {"text_segment": {"end_offset": 173, "start_offset": 156}},
         "display_name": "SpecificDisease"},
        {"text_extraction": {"text_segment": {"end_offset": 179, "start_offset": 176}},
         "display_name": "SpecificDisease"},
        {"text_extraction": {"text_segment": {"end_offset": 246, "start_offset": 243}},
         "display_name": "Modifier"},
        {"text_extraction": {"text_segment": {"end_offset": 340, "start_offset": 337}},
         "display_name": "Modifier"},
        {"text_extraction": {"text_segment": {"end_offset": 698, "start_offset": 695}},
         "display_name": "Modifier"}],
                   "text_snippet": {
                       "content": "1301937\tMolecular basis of hexosaminidase A deficiency and pseudodeficiency in the Berks County Pennsylvania Dutch.\tFollowing the birth of two infants with Tay-Sachs disease ( TSD ) , a non-Jewish , Pennsylvania Dutch kindred was screened for TSD carriers using the biochemical assay . A high frequency of individuals who appeared to be TSD heterozygotes was detected ( Kelly et al . , 1975 ) . Clinical and biochemical evidence suggested that the increased carrier frequency was due to at least two altered alleles for the hexosaminidase A alpha-subunit . We now report two mutant alleles in this Pennsylvania Dutch kindred , and one polymorphism . One allele , reported originally in a French TSD patient ( Akli et al . , 1991 ) , is a GT-- > AT transition at the donor splice-site of intron 9 . The second , a C-- > T transition at nucleotide 739 ( Arg247Trp ) , has been shown by Triggs-Raine et al . ( 1992 ) to be a clinically benign \" pseudodeficient \" allele associated with reduced enzyme activity against artificial substrate . Finally , a polymorphism [ G-- > A ( 759 ) ] , which leaves valine at codon 253 unchanged , is described  .\n "}}

    df = pd.read_csv("../master_data_en.csv")

    for file in pathlib.Path.iterdir(PDF_FOLDER):
        plan_id = int(str(file.absolute()).split('/')[-1].strip().split('.')[0])
        text_content = pdf_to_text(file)
        sample_annotation = {
            "text_extraction": {"text_segment": {"end_offset": 0, "start_offset": 0}},
            "display_name": "None"}
        plan_row = df[df['[idKey]'] == plan_id]['[RateType]']
        rate_type = pd.Series(plan_row).array[0]
        pos = text_content.find(rate_type)
        print("Found @" + str(pos))


def stratify():
    """
    Selecting different suppliers.
    :return:
    """
    df = pd.read_csv("../master_data_en.csv", encoding="utf-8")
    df_minuse = df[df['[MinUsageFeesCredits]'] == True]
    df_minuse_false = df[df['[MinUsageFeesCredits]'] == False]

    objs = []
    objs2 = []

    for a, b in df_minuse.groupby("[RepCompany]"):
        objs.append(b.sample(n=10, replace=True, random_state=1))

    for a, b in df_minuse_false.groupby("[RepCompany]"):
        objs2.append(b.sample(frac=.25, random_state=1))

    df_minuse = pd.concat(objs)
    df_minuse_false = pd.concat(objs2)

    df_merge = pd.concat([df_minuse, df_minuse_false])
    df_merge = df_merge.drop_duplicates()
    return (df_merge)

    # pd.DataFrame(df_concat).to_csv("dataset_rows.csv", index=False, float_format="%.5f")


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
        except Exception as exception:
            pass
        plan_row = df[df['[idKey]'] == plan_id]['[Renewable]']
        print(templ.substitute(filepath=str(file.absolute())))
        text_content = pdf_to_text(filepath=file.absolute())
        print(
            f"Found contract term in text: {text_content.find(str(int(plan_row)))}")


def create_bucket():
    """Creates a new bucket."""
    print("Total PDFs downloaded: ", len(os.listdir("../PDFs")))
    label_pdf_folder = Path("label_pdf")
    if not label_pdf_folder.exists():
        Path.mkdir(label_pdf_folder)
    for file in Path.iterdir(Path(Path(Path.cwd()).parent).joinpath("PDFs")):
        strplan = file.name.strip().split('.pdf')[0]
        in_dataset = int(strplan) in dataset_planids
        if in_dataset:
            if file.name not in os.listdir(label_pdf_folder.name):
                print("Copying PDF")
                shutil.copy(src=str(file), dst=str(label_pdf_folder))


    df = pd.read_csv("../master_data_en.csv")
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob_list = []
    for blob in bucket.list_blobs():
        if "PDF" in blob.name:
            blob_plan_id = str(blob.name).split("/")[-1]
            blob_list.append(blob_plan_id)

    for file in Path.iterdir(label_pdf_folder):
        if file.name not in blob_list:
            source_file_name = str(file)
            destination_blob_name = f"PDF/{file.name}"
            blob = bucket.blob(destination_blob_name)
            blob.upload_from_filename(source_file_name)
            print(f"Uploaded at {destination_blob_name}")


if __name__ == '__main__':
    # df_merge = stratify()
    # df_merge.to_csv("training_set_sample.csv")
    create_jsonl()
