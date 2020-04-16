import requests
from bs4 import BeautifulSoup
import bs4
from texas.utils import *
import os
import warnings
import logging
from urllib3.exceptions import InsecureRequestWarning
from requests.exceptions import MissingSchema, Timeout

PDF_ROOT = "PDFs/"
logging.basicConfig(filename="test.log", level=logging.DEBUG,
                    format='%(asctime)s:%(message)s')

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


def exists(id_key):
    """
    Checks if the pdf has already been downloaded
    :return: boolean
    """
    return os.path.exists(PDF_ROOT + str(id_key) + ".pdf")


def download_pdf(pdf_url, plan):
    """
    Function to download pdf from the URL supplied
    Recursion included.
    :return: Saves the pdf in the PDF folder in the texas folder
    """
    # Checks if the pdf is already downloaded before and if yes then returns 0
    if exists(plan.id_key):
        print("PDF already downloaded, exiting ...")
        return True

    # wraps pdf_url to string for safety
    pdf_url = str(pdf_url)
    # url_extension = str(pdf_url).split('.')[-1].lower()

    print(f"Trying to fetch ID {plan.id_key} and URL {pdf_url} ")
    try:
        try:
            try:
                response = requests.get(url=pdf_url, stream=True, timeout=5)
            except Timeout:
                logging.info(f"Timeout after {TIMEOUT_LIMIT}")
                return False
        except MissingSchema:
            print("\t Invalid URL: ", pdf_url)
            return False
    except requests.exceptions.SSLError:
        # If it throws SSLError, you set verify=False in the argument list for GET
        print(f"\t SSL Error for {plan.id_key}")
        warnings.simplefilter('ignore', InsecureRequestWarning)
        try:
            response = requests.get(url=pdf_url, stream=True, verify=False, timeout=5)
        except Timeout:
            logging.info(f"Timeout after {TIMEOUT_LIMIT}")
            return False

    # content type for finding if its HTML or PDF
    content_type = str(response.headers.get('content-type')).lower()
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
        else:
            print("\t HTML PAGE IFRAME SEARCH")
            frame_element = soup.find("iframe")

            if frame_element:
                pdf_url = frame_element.attrs["src"]
                download_pdf(pdf_url=pdf_url, plan=plan)
            else:
                print("\t IFRAME not Found")

    # if pdf, normally save it
    elif 'application/pdf' in content_type:
        # print("\t Saving but not saving")
        with open(f"{PDF_ROOT}{plan.id_key}.pdf", 'wb') as f:
            f.write(response.content)
