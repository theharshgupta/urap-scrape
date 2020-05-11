
# Residential Electricity Price Scraping - UC Berkeley
Web scraping residential electricity prices in the United States. 

1. Module 1 - Massachusetts
2. Module 2 - New York (Incomplete)
3. Module 3 - Texas (Incomplete)
4. Module 4 - Connecticut

# Installation

1. Download the project repository
```bash
git clone https://github.com/theharshgupta/urap-scrape.git
cd urap-scrape
```
2. Make sure Python 3 is set [Download Python](https://www.python.org/downloads/)

3. Downloading **dependencies**

    1. [Download](https://chromedriver.storage.googleapis.com/index.html?path=76.0.3809.126/) Chromedriver 76 or before (for Mac/Windows/Linux). Unzip this and add `chromedriver` file to the project folder

    2. Install  project dependencies from **`requirements.txt`** using `pip install -r requirements.txt` (make sure when you run this command from your terminal, you are in your project directory)

# Massachussets 
Term: Fall 2019
Links: [energyswitchma.gov](http://www.energyswitchma.gov/#/), [Youtube Demonstration](https://www.youtube.com/watch?v=hpB_RoIlrFI&list=PLpSsC5dbVHV-Uf1VJ2ekMPUIohRoZYe8n&index=1)

### Packages required for running MA
Install everything in `\ma\requirements.txt`

### Quickstart
1. In the **\\ma\\**, open `req_method.py` file.
2. In the `scrape()` function in the file, change the items marked [ACTION REQUIRED] and choose the number of zip codes to analyze.

### Running the script                                           
4. Call  `scrape()` function in the main code block (marked as [ACTION REQUIRED]).
5. After the zip code level CSV file has been downloaded in the `results_MA` folder, you can now replace the main code block to call the function `check_unique()` and can comment out `scrape()`.

# Connecticut
Term: Spring 2020
- The `CT` folder contains all the files necessary for scraping from https://www.energizect.com/compare-energy-suppliers.
- Running `python3 main.py` once inside the `CT` folder will scrape all current plan data and past variable rate data for both EverSource and UI service territories and stores them as CSVs within the data folder.
- You will need `smtplib, ssl, selenium, difflib, time, bs4, os, csv_diff, datetime, csv, json, and a chrome webdriver`.  A majority should come preinstalled with python, but you can install any that you're missing by running `pip install -r requirements.txt` when inside the `urap-scrape` folder.
- The var_parse and var_scrape function should be run at a frequency around once per week in order to get the most updated version of data.

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
1. The `download()` function takes the file path of the CSV.
2. It converts it to a `pandas.Dataframe` and then to a python dictionary for iteration.
3. For each plan in the CSV, a `Plan` class object is created.
4. `texas\pdf.py` recursive function `download_pdf()` takes the URL and the `Plan` object and downloads the PDF to location mentioned at `PDF_ROOT` variable. 

## Zipcode Mapping
The raw CSV from the main website data does not contain zip code information. As a workaround, a request to an official API can be made. 

Function: `map_zipcode()` 

1. A list of recently updated zip codes is fetched from [api.zip-codes.com]([http://api.zip-codes.com/](http://api.zip-codes.com/)) (250 monthly requests).
2. An `API` class object is created with the input list of zip codes. The class constructors calls internal methods to create a Python dictionary (HashMap).
3. For each zipcode, _powertochoose.com_ API is requested which returns data for all the plans in that zip code. Now each of those plans are mapped back to the original CSV, hence creating a HashMap with Plan ID as the Key and List of zip codes as the Value.  
4. A new CSV _master_data_en_zipcodes.csv_ is saved locally that contains an additional column of a list of zip codes for each corresponding plan. 

# New York
Term: Fall 2019
1. Download/Clone the repository to a local folder. Follow the steps here [Github Cloning Repository](https://help.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository)

2. Enter the project folder in the terminal (make sure scrape.py is in your current directory)

3. Run `python3 scrape.py`
