import requests
from bs4 import BeautifulSoup
import bs4
from texas.utils import *
import os
import pdfkit
import warnings
import logging
from urllib3.exceptions import InsecureRequestWarning
from requests.exceptions import MissingSchema, Timeout


"""
Logging Guide 
There are five levels of Logs 
    1. DEBUG: detailed information, of interest when debugging problems
    2. INFO: Confirmation that things work as required 
    3. WARNING (Default): Indication that something unexpected has happened 
       - or some problem that may arise soon - like low disk space.
    4. ERROR: Due to a serious problem, the software errored. 
    5. CRITICAL: A serious error, meaning that program will be unable to run 
"""


def html_to_pdf(url, filepath):
    """
    Executed for URLs that have HTML table.
    :param filepath: Path of the PDF where converted page is saved.
    :param url: URL of the page.
    :return: None.
    """
    platform = sys.platform
    if "win" in platform[0:3]:
        path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
        if not exists(path_wkhtmltopdf):
            path_wkhtmltopdf = r'C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe'
        config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
        pdfkit.from_url(url, filepath, configuration=config, options={'quiet': ''})
    elif platform == "darwin":
        pdfkit.from_url(url, filepath, options={'quiet': ''})


def download_pdf_concurrent(plan):
    try:
        result = download_pdf(pdf_url=plan.facts_url, plan=plan)
        return result
    except Exception as e:
        print(e)
        return



def download_pdf(pdf_url, plan):
    """
    Function to download pdf from the URL supplied
    Recursion included.
    :return: Saves the pdf in the PDF folder in the texas folder
    """
    # Checks if the pdf is already downloaded before and if yes then returns 0
    # Added timestamp to the PDF filename
    # Even if the pdf is downloaded, we still need to download the pdf for the new plan. Because
    # if the plan is updated then it's PDF will also be updated.
    pdf_filepath = f"{os.path.join(PDF_DIR, str(plan.id_key))}-{get_datetime().replace('_', '-')}.pdf"

    print(f"Trying to download {plan.id_key} at {pdf_url} ")
    # if "sparkenergy.com" in pdf_url and ".pdf" in pdf_url[-4:]:
    #     from selenium import webdriver
    #     download_dir = "X:/Python/urap-scrape/texas"
    #     options = webdriver.ChromeOptions()
    #     profile = {"plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}],
    #                "download.default_directory": download_dir, "download.extensions_to_open": "applications/pdf",
    #                'download.prompt_for_download': False, 'download.directory_upgrage': True,
    #                'profile.default_content_settings.popups': 0,
    #                }
    #
    #     options.add_experimental_option("prefs", profile)
    #     driver = webdriver.Chrome('C:\\chromedriver.exe',
    #                               chrome_options=options)  # Optional argument, if not specified will search path.
    #
    #     driver.get(pdf_url)
    #
    #     # response = requests.get(pdf_url)
    #     # print(response.status_code)
    #     # print(response.content)
    #     # print(len(response.content))
    #     # if len(response.content) > 0:
    #     #     with open(f"{os.path.join(PDF_DIR, str(plan.id_key))}.pdf", 'wb') as f:
    #     #         f.write(response.content)
    #     # else:
    #     #     logging.info(f"ERROR - 0 BYTES IN THE PDF CONTENT {plan.id_key} URL {plan.facts_url}")
    #     # return

    try:
        try:
            try:
                response = requests.get(url=pdf_url, stream=True, timeout=60)
            except Timeout:
                logging.info(f"Timeout after {TIMEOUT_LIMIT}")
                return
        except MissingSchema:
            print("\t Invalid URL: ", pdf_url)
            return False
    except requests.exceptions.SSLError:
        # If it throws SSLError, you set verify=False in the argument list for GET
        print(f"\t SSL Error for {plan.id_key}")
        warnings.simplefilter('ignore', InsecureRequestWarning)
        try:
            response = requests.get(url=pdf_url, stream=True, verify=False, timeout=60)
        except Timeout:
            logging.info(f"Timeout after {TIMEOUT_LIMIT}")
            return False

    # content type for finding if its HTML or PDF
    content_type = str(response.headers.get('content-type')).lower()
    print("\t", content_type)
    # if HTML extract embedded or specific URL through beautifulSoup
    if 'text/html' in content_type:
        print(f"\t Fetching an HTML")
        soup = BeautifulSoup(response.text, 'html.parser')
        if "neccoopenergy" in pdf_url:
            print("\t Fetching a Neccoopenergy PDF file. ")
            try:
                pdf_element = soup.find(id='current_tos')
                pdf_url = pdf_element.attrs["href"]
                download_pdf(pdf_url=pdf_url, plan=plan)
            except Exception as e:
                print("\t The PDF could not be downloaded. :(")
                return
        else:
            frame_element = soup.find("iframe")
            table_exists = soup.find("table")
            if frame_element:
                pdf_url = frame_element.attrs["src"]
                logging.info(f"Extracting in frame PDF at {plan.facts_url} calling recursively.")
                download_pdf(pdf_url=pdf_url, plan=plan)
            elif table_exists and (soup.body.findAll(text=HTML_KEYWORDS[0] or soup.body.findAll(text=HTML_KEYWORDS[1]))):
                # html_to_pdf(url=pdf_url, filepath=f"{os.path.join(PDF_DIR, str(plan.id_key))}.pdf")
                html_to_pdf(url=pdf_url, filepath=pdf_filepath)
                logging.info(f"Converting HTML for {plan.facts_url} to PDF")
            else:
                print("\t HTML nothing found.")

    elif 'application/pdf' in content_type:
        if len(response.content) > 0:
            # with open(f"{os.path.join(PDF_DIR, str(plan.id_key))}.pdf", 'wb') as f:
            with open(pdf_filepath, 'wb') as f:
                f.write(response.content)
        else:
            logging.info(f"ERROR - 0 BYTES IN THE PDF CONTENT {plan.id_key} URL {plan.facts_url}")

    if exists(pdf_filepath):
        print("\t Downloaded Successfully.")
        logging.info(f"Successfully downloaded {plan.id_key}.")
        return pdf_filepath
    else:
        logging.info(f"Could not download {plan.id_key}.")
        return

