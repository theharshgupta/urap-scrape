
# Texas 
Term: Spring 2020 

Links: [http://powertochoose.org/](http://powertochoose.org/)

The `texas` module folder contains all the files for scraping plans. `texas\efl` contains scripts for PDF parsing.

## _PDF Parsing_
### Model
The project uses Google AutoML Vision (Entity Extraction) to build a machine learning based PDF parser. [Here](https://cloud.google.com/natural-language/automl/docs/quickstart) is a quickstart guide for AutoML. 

### Training 
PDFs are manually labelled using AutoML dashboard UI. All the PDFs for labelling, training and testing are uploaded in [Buckets](https://cloud.google.com/storage/docs/listing-buckets#storage-list-buckets-python) with Google Storage.  

`efl\main.py` Creates the storage bucket objects of PDFs, [JSONLines](http://jsonlines.org/) (different from JSON) file, and CSV and then uploads them to the cloud. The `stratify()` function selects different data rows from the raw CSV for labeling and training.  

### Running the script 
Authorized users can generate `credentials.json` from the Google Console and run `google.cloud` module in the script to run aforementioned functions. 

## _Scrape_
`texas\main.py` manipulates data of a locally stored CSV of all the plans (downloaded from the main website).  First, Spanish data rows are filtered and some columns are deleted from the downloaded CSV. 
### PDF Downloading 
1. The `download()` function takes the file path of the CSV.
2. It converts it to a `pandas.Dataframe` and then to a python dictionary for iteration.
3. For each plan in the CSV, a `Plan` class object is created.
4. `texas\pdf.py` recursive function `download_pdf()` takes the URL and the `Plan` object and downloads the PDF to location mentioned at `PDF_ROOT` variable. 

## _Zipcode Mapping_
The raw CSV from the main website data does not contain zip code information. As a workaround, a request to an official API can be made. 

Zipcode mapping process uses parallel processing (multiprocessing) to use multiple cores to accelerate the speed. With the `futures` module, we set `ProcessPool`. To get started with concurrency: 

1. Install `futures` module with `pip install futures`
2. Install `multiprocessing` module with `pip install multiprocessing`


Function: `map_zipcode()` 

1. A list of recently updated zip codes is fetched from [api.zip-codes.com]([http://api.zip-codes.com/](http://api.zip-codes.com/)) (250 monthly requests).
2. An `API` class object is created with the input list of zip codes. The class constructors calls internal methods to create a Python dictionary (HashMap).
3. For each zipcode, _powertochoose.com_ API is requested which returns data for all the plans in that zip code. Now each of those plans are mapped back to the original CSV, hence creating a HashMap with Plan ID as the Key and List of zip codes as the Value.  
4. A new CSV _master_data_en_zipcodes.csv_ is saved locally that contains an additional column of a list of zip codes for each corresponding plan. 

## APIs (& other ways to get data)
Texas has multiple endpoints for their APIs. Each API returns different results, with some overlapping data. 

1. http://powertochoose.com/en-us/service/v1/ : Internal API calls are made here. On PTC home screen, zipcode checking is preformed using this API. The parameters in the `post` request are: `{method: "plans/count", plan_type: 1, zip_code: "75001", include_details: false, language: 0}`. On inspection, one can see that the `method` key can take different parameters that yields different results. When this API endpoint was tested for `{"method":"plans","plan_type":1,"zip_code":"75001","include_details":True,"language":0}` it returns all the plan details. Further inspection shows that for `{"method": "TduCompaniesByZip", "zip_code": "75001", "include_details": False, "language": 0}`, the API returns the list of TDUs in that zip code. 
2. http://api.powertochoose.org/api/PowerToChoose/plans?zip_code=: Using this end point, you can add a zipcode and it returns XML data, properly formatted which contains almost similar amount of data. It takes a little longer than the first API endpoint. 
3. Exporting CSV: http://www.powertochoose.org/en-us/Plan/ExportToCsv downloads the most recent plan information available on the website. This is the fastest way to download formatted CSV data. However, zip code information is unavailable with this method. 


Tools:
5. Good markdown editor: https://stackedit.io/

