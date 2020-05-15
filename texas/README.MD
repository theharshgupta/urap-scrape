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
`texas\main.py` manipulates data of a locally stored CSV of all the plans (downloaded from the main website).  First, Spanish data rows are filtered from the downloaded CSV. 
### PDF Downloading 
1. The `download()` function takes the file path of the CSV.
2. It converts it to a `pandas.Dataframe` and then to a python dictionary for iteration.
3. For each plan in the CSV, a `Plan` class object is created.
4. `texas\pdf.py` recursive function `download_pdf()` takes the URL and the `Plan` object and downloads the PDF to location mentioned at `PDF_ROOT` variable. 

## _Zipcode Mapping_
The raw CSV from the main website data does not contain zip code information. As a workaround, a request to an official API can be made. 

Function: `map_zipcode()` 

1. A list of recently updated zip codes is fetched from [api.zip-codes.com]([http://api.zip-codes.com/](http://api.zip-codes.com/)) (250 monthly requests).
2. An `API` class object is created with the input list of zip codes. The class constructors calls internal methods to create a Python dictionary (HashMap).
3. For each zipcode, _powertochoose.com_ API is requested which returns data for all the plans in that zip code. Now each of those plans are mapped back to the original CSV, hence creating a HashMap with Plan ID as the Key and List of zip codes as the Value.  
4. A new CSV _master_data_en_zipcodes.csv_ is saved locally that contains an additional column of a list of zip codes for each corresponding plan. 
