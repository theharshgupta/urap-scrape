import requests, sys, json
import time, os, pdfkit, re
from bs4 import BeautifulSoup
from sys import platform
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import texas.pdfReader

sys.path.append('..')
from email_service import send_email

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


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
    link = 'http://api.powertochoose.org/api/PowerToChoose/plans?zip_code=' + str(
        zip_code)
    response = requests.get(link, verify=False)
    return response.text


def getJSON(zip_code):
    """
        return a JSON object containing data from the given zip code
    """
    response = getResponseText(zip_code)
    return json.loads(response)


def getEmbeddedPDFLink(url):
    """
        if there's any embedded links to PDFs, get it
        returns: if there's a PDF in 'url', returns that
                 if not, return the input 'url'

        purpose: some companies had PDFs embedded on their pages, so when I downloaded it, it was failing
    """
    try:
        txt = requests.get(url, verify=False)
        # I'm searching for a URL that is length [10, 100]
        # without having bounds can capture non-URLs
        match = re.search("https?://.{10,100}\.pdf", txt.text)
        return match.group() if match else url
    except Exception as e:
        print("failed to get embedded link:", e)
        return url


def isFileExists(folder_name, file_name_with_extension):
    """
        returns: true if file given by the parameters exists, false otherwise
    """
    return os.path.exists(folder_name + file_name_with_extension)


def getUniquePath(folder_name, preferred_file_name):
    """
        initial is the name of the file without the extension
    """
    if not isFileExists(folder_name, preferred_file_name + ".pdf"):
        return folder_name + preferred_file_name + ".pdf"
    count = 1
    while (
    isFileExists(folder_name, preferred_file_name + "-" + str(count) + ".pdf")):
        count += 1
    return folder_name + preferred_file_name + "-" + str(count) + ".pdf"


def downloadPDF(link, preferred_file_name, folderName):
    """
        given an url to a pdf file on a webpage,
        download the pdf file locally
    """
    path = getUniquePath(folderName, preferred_file_name)
    try:
        # verify basically bypasses SSl verification
        # there are times where setting it to True will prevent
        # certain PDFs from downloading
        content = requests.get(link, verify=False).content
        f = open(path, 'wb')
        f.write(content)
        f.close()
    except requests.exceptions.ConnectionError:
        print("HTTP Connection error:", link)
        downloadUsingPDFKit(link, path)

    # check if the pdf was downloaded successfully
    if len(pdfReader.getPDFasText(path, False)) < 10:
        downloadUsingPDFKit(link, path)
    return path


def redownloadPDF(downloadedPath, link=""):
    """
        Call this function if you redownload the PDF given by downloadedPath
        downloadedPath: the path (not the URL), such as "PDFs/Power Next.pdf"
    """
    print("redownloading", downloadedPath)

    # finding the associated URL to the pdf file
    # the reason we have this is because redownloadPDF is called from pdfReader without knowing the URL
    if link == "":
        from csv_generate import fact_sheet_paths, terms_of_service_paths
        # determining if it's a fact sheet or a terms of service
        m = fact_sheet_paths if downloadedPath.split("/")[
                                    0] == "PDFs" else terms_of_service_paths
        for key in m:
            if m[key] == downloadedPath:
                link = key
                break
    # override the currently downloaded (most likely corrupted) pdf file
    downloadUsingPDFKit(link, downloadedPath)


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
        if platform == "win32" or platform == "cygwin":
            # IMPORTANT: this path might vary across different windows machines
            # make sure it matches to the path where tesseract is located
            config = pdfkit.configuration(
                wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
            pdfkit.from_url(link, path, configuration=config)
        else:
            pdfkit.from_url(link, path)
    except Exception as e:
        print("pdfkit was not able download,", link)
        print(e)
        send_email("failed to download " + link + "\nexception text: " + str(e))


# unit tests
if __name__ == "__main__":
    # this is example of a webpage that this method doesn't work on
    # downloadUsingPDFKit("https://www.4changeenergy.com/viewpdf.aspx/?Docs/efl_budsva12gad_o.pdf", "./PDFs/", "doesnt_work.pdf")
    # downloadPDF(getEmbeddedPDFLink("https://www.myexpressenergy.com/viewpdf.aspx/?Docs/efl_fastva12gab_o.pdf"), "doesnt_work", "PDFs/")
    # it works in all other cases
    # downloadUsingPDFKit("https://newpowertx.com/EmailHTML/efl.aspx?RateID=672&BrandID=5&PromoCodeID=446", "./PDFs/works.pdf", "PDFs/")
    # downloadPDF(getEmbeddedPDFLink("https://www.libertypowercorp.com/wp-content/uploads/2018/07/TCC_TX.pdf"), "works", "PDFs/")
    # print(getEmbeddedPDFLink("https://www.myexpressenergy.com/viewpdf.aspx/?Docs/efl_fastva12gab_o.pdf"))
    # downloadUsingPDFKit("https://newpowertx.com/EmailHTML/efl.aspx?RateID=677&BrandID=5&PromoCodeID=447", "PDFs/hello.pdf")
    # redownloadPDF("PDFs/New Power Texas-1.pdf", "https://newpowertx.com/EmailHTML/efl.aspx?RateID=662&BrandID=5&PromoCodeID=446")
    downloadPDF(getEmbeddedPDFLink(
        "https://newpowertx.com/EmailHTML/efl.aspx?RateID=662&BrandID=5&PromoCodeID=446"),
                "w", "PDFs/")
