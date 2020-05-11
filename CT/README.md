# Connecticut
Term: Spring 2020
- The `CT` folder contains all the files necessary for scraping from https://www.energizect.com/compare-energy-suppliers.
- Running `python3 main.py` once inside the `CT` folder will scrape all current plan data and past variable rate data for both EverSource and UI service territories and stores them as CSVs within the data folder.
- You will need `smtplib, ssl, selenium, difflib, time, bs4, os, csv_diff, datetime, csv, json, and a chrome webdriver`.  A majority should come preinstalled with python, but you can install any that you're missing by running `pip install -r requirements.txt` when inside the `urap-scrape` folder.
- The var_parse and var_scrape function should be run at a frequency around once per week in order to get the most updated version of data.
