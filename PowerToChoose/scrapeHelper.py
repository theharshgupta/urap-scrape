import requests, sys, json
import time, os, pdfkit
from pdfReader import isPDFFile
from bs4 import BeautifulSoup

def getCurrentDate():
    """
        >>> getCurrentDate()
        9/22/2019
    """
    import datetime
    now = datetime.datetime.now()
    return str.format("{}/{}/{}", now.month, now.day, now.year)

def getResponseText(zip_code):
    """
    Send an API request to PowerToChoose and return the response
    Input:  1)  the zip code of the city
    """
    link = 'http://api.powertochoose.org/api/PowerToChoose/plans?zip_code=' + str(zip_code)
    response = requests.get(link, verify=False)
    return response.text

def getJsonFromZIP(zip_code):
    """
        return a JSON object containing data from the given zip code
    """
    response = getResponseText(zip_code)
    return json.loads(response)

def isFileExists(folder_name, file_name_with_extension):
    return os.path.exists(folder_name + file_name_with_extension)

def getUniquePath(folder_name, preferred_file_name):
    """
    initial is the name of the file without the extension
    """
    if not isFileExists(folder_name, preferred_file_name + ".pdf"):
        return folder_name + preferred_file_name + ".pdf"
    count = 1
    while(isFileExists(folder_name, preferred_file_name + "-" + str(count) + ".pdf")):
        count += 1
    return folder_name + preferred_file_name + "-" + str(count) + ".pdf"
    

def downloadPDF(link, preferred_file_name, folderName):
    """
    given an url to a pdf file on a webpage,
    download the pdf file locally
    """
    path = getUniquePath(folderName, preferred_file_name)
    try:
        content = requests.get(link).content
        f = open(path, 'wb')
        f.write(content)
        f.close()
        print(preferred_file_name, link)
    except requests.exceptions.ConnectionError:
        print("HTTP Connection error:", link)
        downloadUsingPDFKit(link, path)
    return path


def downloadUsingPDFKit(link, path):
    """
        There was no reason to use selenium to download pdfs, instead I found this library called pdfkit
        pdfkit will convert HTML pages to PDFs, some webpages they have HTML files instead of PDFs,
        so pdfkit fixes the problem of converting those HTML pages to PDFs and downloading them

        pdfkit depends on wkhtmltopdf
        to install pdfkit: run "pip install pdfkit"
        to install wkhtmltopdf: go to "https://wkhtmltopdf.org/downloads.html"
    """
    try:
        pdfkit.from_url(link, path)
    except Exception:
        print("pdfkit was not able download,", link)

if __name__ == "__main__":
    # this is example of a webpage that this method doesn't work on
    #downloadUsingPDFKit("https://www.4changeenergy.com/viewpdf.aspx/?Docs/efl_budsva12gad_o.pdf", "./PDFs/", "doesnt_work.pdf")
    downloadUsingPDFKit("https://docs.championenergyservices.com/ExternalDocs?planname=PN2402&state=TX&language=EN", "./PDFs/doesnt_work.pdf")
    # it works in all other cases
    downloadUsingPDFKit("https://newpowertx.com/EmailHTML/efl.aspx?RateID=672&BrandID=5&PromoCodeID=446", "./PDFs/works.pdf")
