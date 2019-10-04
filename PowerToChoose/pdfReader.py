import PyPDF2, re, os

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

    output = ""
    try:
        pdfReader = PyPDF2.PdfFileReader(open(path, 'rb'))
        for i in range(pdfReader.numPages):
            page = pdfReader.getPage(i)
            output += page.extractText()
    except PyPDF2.utils.PdfReadError:
        pass
        #print(path, "is a malformed PDF")
    except OSError:
        pass
        #print("OSError when reading", path)

    noNewLines = " ".join(output.split("\n")) # replace new lines with space
    return noNewLines


def getTerminationFee(txt):
    """
        extract a termination fee from the PDF
    """
    pattern = "[Tt]ermination [Ff]ee.*"
    match = re.search(pattern, txt)
    if match:
        # searching for the closest dollar value where 'termination fee' was found
        fee_with_details = re.search(r"(?P<amount>\$\d+ [a-z]+[^.!?]*[.!?])", match.group())
        if fee_with_details:
            return fee_with_details.group()
        
        fee_match = re.search(r"(?P<amount>\$\d+)", match.group())
        if fee_match:
            return fee_match.group("amount")

    return "N/A"
    

if __name__ == "__main__":
    all_pdfs = [f for f in os.listdir("PDFs/") if os.path.isfile("PDFs/" + f) and isPDFFile(f)]

    for pdf in all_pdfs:
        txt = getPDFasText("PDFs/" + pdf)
        print("Termination fee:", getTerminationFee(txt))


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