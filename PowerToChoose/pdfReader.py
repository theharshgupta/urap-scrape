import PyPDF2, re, os
import scrapeHelper

def isPDFFile(fileName):
    """
        checks whether fileName is a pdf file
        fileName is a PDF file, if the extension is .pdf
    """
    return len(fileName) >= 4 and fileName[-4:] == ".pdf"


def getPDFasText(path):
    """
        path: must be in the format parentFolder + fileName + extension
        example of valid paths:
            1) PDFs/AMBIT ENERGY.pdf
            2) PDFs/Energy to Go.pdf

        returns: The text representation of the given PDF file

        It reads the PDF file using PyPDF2 library and gets the PDF file as a string
    """

    def getAsStr(reader):
        out = ""
        for i in range(pdfReader.numPages):
            page = pdfReader.getPage(i)
            out += page.extractText()
        return out
    
    def readPDF():
        try:
            pdfReader = PyPDF2.PdfFileReader(open(path, 'rb'))
            return getAsStr(pdfReader)
        except Exception:
            pass

    output = ""
    try:
        pdfReader = PyPDF2.PdfFileReader(open(path, 'rb'))
        output = getAsStr(pdfReader)
    except PyPDF2.utils.PdfReadError:
        #print(path, "is a malformed PDF")
        scrapeHelper.redownloadPDF(path)
        readPDF()
    except OSError:
        #print("OSError when reading", path)
        scrapeHelper.redownloadPDF(path)
        readPDF()
        
    noNewLines = " ".join(output.split("\n") if output else "") # replace new lines with space
    return noNewLines


def getTerminationFee(txt, fee):
    """
        extract a termination fee from the PDF
    """    

    # sometimes fee is passed in format like "20/month remaining" or "20.00 month remaining"
    fee = fee.split(".")[0]
    try:
        fee = int(float(fee))
    except ValueError:
        fee = re.search("\d+", fee).group()

    match = re.search("[Tt]ermination [Ff]ee\s*[A-Za-z.,\s]*\?.*", txt)
    if match:
        match = re.search("[A-Z]?[a-z]*[.,!?]*\s*\$\s*" + str(fee) + "\.*\d*\s*[A-Za-z\s,'()\$\d]*[.!]*", match.group())
        if match:
            return match.group()
    
    # if we still haven't found the details, then use these regular expressions
    patterns = ["[A-Z]?[a-z]*[.,!?]*\s*\$\s*" + str(fee) + "\.*\d*\s*[A-Za-z\s,']*[.!]*",
                "\?\s*[A-Za-z.,\s]*\$\s*" + str(fee) + "\.*\d*\s*[A-Za-z\s,']*[.!]*", 
                "\?\s*[A-Za-z.,\s\$\d]*[A-Z]?[a-z]*[.,!?]*\s*[Tt]ermination [Ff]ee\s*[A-Za-z\s,']*[.!]*"]
    for pattern in patterns:
        match = re.search(pattern, txt)
        if match:
            return match.group()
    return "N/A"


"""
if __name__ == "__main__":
    all_pdfs = [f for f in os.listdir("PDFs/") if os.path.isfile("PDFs/" + f) and isPDFFile(f)]

    for pdf in all_pdfs:
        txt = getPDFasText("PDFs/" + pdf)
        print(pdf, getTerminationFee(txt), "\n\n")
"""

""" Example 1 of a unreadable PDF
txt = getPDFasText("PDFs/Texans Energy.pdf")
print("Length of PDF:", len(txt))
fee = getTerminationFee(txt)
print(fee)

# Example 2 of a unreadable PDF
txt2 = getPDFasText("PDFs/AMBIT ENERGY.pdf")
print("Length of PDF:", len(txt2))
fee2 = getTerminationFee(txt2)
print(fee2)
"""