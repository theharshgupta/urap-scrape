
# Installation

1. Download the project repository
```bash
git clone https://github.com/theharshgupta/urap-scrape.git
cd urap-scrape
```
2. Make sure Python 3 is set [Download Python](https://www.python.org/downloads/)
# Texas 
Term: Spring 2020
Links: [http://powertochoose.org/](http://powertochoose.org/)
The `texas` module folder contains all the files for scraping plans. `texas\efl` contains scripts for PDF parsing.

## PDF Parsing
### Model
The project uses Google AutoML Vision (Entity Extraction) to build a machine learning based PDF parser. [Here]([https://cloud.google.com/natural-language/automl/docs/quickstart](https://cloud.google.com/natural-language/automl/docs/quickstart)) is a quickstart guide for AutoML. 

### Training 
PDFs are manually labelled using AutoML dashboard UI. All the PDFs for labelling, training and testing are uploaded in [Buckets]([https://cloud.google.com/storage/docs/listing-buckets#storage-list-buckets-python](https://cloud.google.com/storage/docs/listing-buckets#storage-list-buckets-python)) with Google Storage.  

`efl\main.py` Creates the storage bucket objects of PDFs, [JSONLines]([http://jsonlines.org/](http://jsonlines.org/)) (different from JSON) file, and CSV and then uploads them to the cloud. The `stratify()` function selects different data rows from the raw CSV for labeling and training.  

### Running the script 
Authorized users can generate `credentials.json` from the Google Console and run `google.cloud` module in the script to run aforementioned functions. 

## Scrape
`texas\main.py` manipulates data of a locally stored CSV of all the plans (downloaded from the main website).  First, Spanish data rows are filtered from the downloaded CSV. 
### PDF Downloading 
1. The `parse_csv` function takes the file path of the CSV 

