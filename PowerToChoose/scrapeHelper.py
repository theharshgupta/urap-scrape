import requests, sys, json
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

def downloadPDF(link, fileName, folderName):
    """
    given an url to a pdf file on a webpage,
    download the pdf file locally
    """
    with open(folderName + fileName + ".pdf", 'wb') as f:
        try:
            f.write(requests.get(link).content)
            print(fileName, "downloaded")
        except requests.exceptions.ConnectionError:
            print("HTTP Connection error:", link)
