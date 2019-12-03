# Residential Electricity Price Scraping - UC Berkeley
A repository for web scraping for URAP research project - Investigationg residential electricity prices in the US


# Module - Massachussets - [Youtube Demo](https://www.youtube.com/watch?v=hpB_RoIlrFI&list=PLpSsC5dbVHV-Uf1VJ2ekMPUIohRoZYe8n&index=1)

## Installation

1. Download the project repository
```bash
git clone https://github.com/theharshgupta/urap-scrape.git
cd urap-scrape
```
2. Make sure Python 3 is set [Download Python](https://www.python.org/downloads/)

3. Downloading **dependencies** 

    1. [Download](https://chromedriver.storage.googleapis.com/index.html?path=76.0.3809.126/) Chromedriver 76 or before (for Mac/Windows/Linux). Unzip this and add `chromedriver` file to the project folder
    
    2. Install  project dependencies from **`requirements.txt`** using `pip install -r requirements.txt` (make sure when you run this command from your terminal, you are in your project directory)

### Quickstart 
**Scraping results from [energyswitchma.gov](http://www.energyswitchma.gov/#/)**

1. In the **root directory**, open `req_method.py` file. 
2. In the `scrape()` function in the file, change the items marked \[ACTION REQUIRED\]
3. Under that block of code, you can run two different piece of code. The code to check for unique entries can only be run after the zipcode level data is downloaded. 

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

### New York 

1. Download/Clone the repository to a local folder. Follow the steps here [Github Cloning Repository](https://help.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository)

2. Enter the project folder in the terminal (make sure scrape.py is in your current directory)

3. Run `python3 scrape.py`


## Module 2 - Power to Choose  

### Dependencies

| Name          | Installation Link                             | Purpose                                   |
| :---          |    :----:                                     |          ---:                             |
| Poppler       | https://poppler.freedesktop.org               | Used to perform OCR on PDfs               |
| wkhtmltopdf   | https://docs.bitnami.com/installer/apps/odoo/configuration/install-wkhtmltopdf/        | Used to convert HTML pages into PDFs      |

### Run

**NOTE: the scripts need to be executed from the PowerToChoose folder or else it will fail**

from the project folder, run:
```
cd PowerToChoose
python csv_generate.py <zip_code> <number_of_plans>
```

example:
`python csv_generate.py 75001 10`
