# Residential Electricity Price Scraping - UC Berkeley
A repository for web scraping for URAP research project - Investigationg residential electricity prices in the US

Currently, this project is for 4 states

1. Module 1 - Massachussets
2. Module 2 - New York
3. Module 3 - Texas
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

# Module 1 - Massachussets - [Youtube Demo](https://www.youtube.com/watch?v=hpB_RoIlrFI&list=PLpSsC5dbVHV-Uf1VJ2ekMPUIohRoZYe8n&index=1)

### Quickstart
**Scraping results from [energyswitchma.gov](http://www.energyswitchma.gov/#/)**

1. In the **root directory**, open `req_method.py` file.
2. In the `scrape()` function in the file, change the items marked **\[ACTION REQUIRED\]** and choose how many zipcodes you want to run the script for.

### Scraping the data                                           
4. You can just call the function `scrape` by writing `scrape()` in the main code block as mentioned in the previous step.
5. After the zipcode level csv have been downloaded in the result_MA folder, you can now replace the main code block to call the function `check_unique()` and can comment out `scrape`.
## Packages required for running MA

1. requests module
2. pandas (if you dont have pandas, just run pip3 install pandas)
3. pathlib
4. json
5. glob
6. datetime

By default you should have all the modules except pandas. Pandas is a big package and may take some minutes to get installed.

# Module 2 - New York

1. Download/Clone the repository to a local folder. Follow the steps here [Github Cloning Repository](https://help.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository)

2. Enter the project folder in the terminal (make sure scrape.py is in your current directory)

3. Run `python3 scrape.py`


# Module 3 - Texas - Spring 2020
The `texas` module folder contains all the files for scraping plans. `texas\efl` contains scripts for PDF parsing.

# Module 4 CT - Spring 2020
- The `CT` folder contains all the files necessary for scraping from https://www.energizect.com/compare-energy-suppliers.
- Running `python3 main.py` once inside the `CT` folder will scrape all current plan data and past variable rate data for both EverSource and UI service territories and stores them as CSVs within the data folder.
- You will need `smtplib, ssl, selenium, difflib, time, bs4, os, csv_diff, datetime, csv, json, and a chrome webdriver`.  A majority should come preinstalled with python, but you can install any that you're missing by running `pip install -r requirements.txt` when inside the `urap-scrape` folder.





# DEPRECATED - Texas - Fall 2019

#### Dependencies

| Name          | Installation Link                             | Purpose                                   |
| :---          |    :----:                                     |          :---:                            |
| Poppler       | https://poppler.freedesktop.org               | Used to perform OCR on PDfs               |
| wkhtmltopdf   | https://docs.bitnami.com/installer/apps/odoo/configuration/install-wkhtmltopdf/        | Used to convert HTML pages into PDFs      |

#### Possible Errors

| Name          | Meaning                             | Fix                                   | Where |
| :---          |    :---:                           |          ---:                          | ---:  |
| TesseractNotFound | Invalid path to Tesseract | [link](https://stackoverflow.com/questions/50951955/pytesseract-tesseractnotfound-error-tesseract-is-not-installed-or-its-not-i) | ocr() function in pdfReader.py |
| No wkhtmltopdf executable found | Invalid path to wkhtmltopdf | [link](https://stackoverflow.com/questions/27673870/cant-create-pdf-using-python-pdfkit-error-no-wkhtmltopdf-executable-found) | downloadUsingPDFKit() function in scrapeHelpers.py |

#### Run

**NOTE: the scripts need to be executed from the PowerToChoose folder or else it will fail**

**IMPORTANT: make sure you have folders named "PDFs" and "Terms of Services" in the "PowerToChoose" folder (case-sensitive)**

from the project folder, run:
```
cd PowerToChoose
python csv_generate.py <zip_code> <number_of_plans>
```

example:
`python csv_generate.py 75001 10`
