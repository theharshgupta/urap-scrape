import requests
from bs4 import BeautifulSoup
import bs4
import os
import warnings
from urllib3.exceptions import InsecureRequestWarning
from requests.exceptions import MissingSchema


PDF_ROOT = "PDFs/"


def exists(id_key):
    """
    Checks if the pdf has already been downloaded
    :return: boolean
    """
    return os.path.exists(PDF_ROOT + id_key + ".pdf")


def download_pdf(pdf_url, plan):
    """
    Function to download pdf from the URL supplied
    Recursion included.
    :return: Saves the pdf in the PDF folder in the texas folder
    """
    # Checks if the pdf is already downloaded before and if yes then returns 0
    if exists(plan.idKey):
        print("PDF already downloaded, exiting ...")
        return 0

    # wraps pdf_url to string for safety
    pdf_url = str(pdf_url)
    # url_extension = str(pdf_url).split('.')[-1].lower()

    print(f"Trying to fetch ID {plan.idKey} and URL {pdf_url} ")
    try:
        # if website does not throw a SSLError
        try:
            response = requests.get(url=pdf_url, stream=True)
        except MissingSchema:
            print("\t Invalid URL: ", pdf_url)
            return False
    except requests.exceptions.SSLError:
        # If it throws SSLError, you set verify=False in the argument list for GET
        print(f"\t SSL Error for {plan.idKey}")
        warnings.simplefilter('ignore', InsecureRequestWarning)
        response = requests.get(url=pdf_url, stream=True, verify=False)

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
        with open(f"{PDF_ROOT}{plan.idKey}.pdf", 'wb') as f:
            f.write(response.content)
