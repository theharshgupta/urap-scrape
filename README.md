
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
[Instructions](https://github.com/theharshgupta/urap-scrape/tree/master/texas)

# New York
Term: Fall 2019
1. Download/Clone the repository to a local folder. Follow the steps here [Github Cloning Repository](https://help.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository)

2. Enter the project folder in the terminal (make sure scrape.py is in your current directory)

3. Run `python3 scrape.py`
