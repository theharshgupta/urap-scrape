import PyPDF2, re, os, sys
import scrapeHelper
import pytesseract 
from PIL import Image 
from pdf2image import convert_from_path

def isPDFFile(fileName):
    """
        checks whether fileName is a pdf file
        fileName is a PDF file, if the extension is .pdf
    """
    return len(fileName) >= 4 and fileName[-4:] == ".pdf"


def ocr(pdfPath):
    try:
        pages = convert_from_path(pdfPath, 500)
    except Exception as e:
        return ""
    pdfName = pdfPath.split(".pdf")[0]
    image_counter = 1

    for page in pages: 
        filename = pdfName+"_"+str(image_counter)+".jpg"
        
        # Save the image of the page in system 
        page.save(filename, 'JPEG') 
    
        image_counter = image_counter + 1
    
    # Iterate from 1 to total number of pages 
    text = ""
    for i in range(1, image_counter): 
        filename = pdfName+"_"+str(i)+".jpg"

        # Recognize the text as string in image using pytesserct 
        text += str(((pytesseract.image_to_string(Image.open(filename))))) 
    return text
    

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
            return ""

    output = ""
    try:
        pdfReader = PyPDF2.PdfFileReader(open(path, 'rb'))
        output = getAsStr(pdfReader)
    except Exception:
        scrapeHelper.redownloadPDF(path)
        output = readPDF()
    
    # assuming if length is < 50, then the pdf library failed
    # so then we try OCR on it
    if len(output) < 10:
        print("PDF library most likely failed, running OCR on", path)
        try:
            output = ocr(path)
        except Image.DecompressionBombError:
            print("error")
        except Image.DecompressionBombWarning:
            print("error")

    output = output.replace('-\n', '')
    noNewLines = " ".join(output.split("\n")) # replace new lines with space
    return noNewLines


def getTerminationFee(txt, fee):
    """
        extract a termination fee from the PDF
    """

    # assuming the PDf file is empty, 10 is arbitrary
    if len(txt) < 10:
        return "PDF corrupted"

    # sometimes fee is passed in format like "20/month remaining" or "20.00 month remaining"
    # we only want the value 20 in that case
    fee = fee.split(".")[0]
    try:
        fee = int(float(fee))
    except ValueError:
        m = re.search("\d+", fee)
        if m:
            fee = m.group()
        else:
            print("fee not found", fee)

    # TODO: use this "['’`\dA-Za-z\s,_:\(\);\-\"\$\%]+"
    match = re.search("[Tt]ermination [Ff]ee\s*[A-Za-z.,\s]*\?.*", txt)
    if match:
        match = re.search("[A-Z]?[a-z]*[.,!;]*[\sA-Za-z]*\$\s*" + str(fee) + "\.*\d*\s*[A-Za-z\s,'()\$\d]*[.!]*", match.group())
        if match:
            # many PDFs have "Can my price change during contract pediod?" in common, not separated from the termination feein common
            return "1: " + match.group().split("Can my price")[0]
    
    # if we still haven't found the details, then use these regular expressions
    patterns = ["[A-Z]?[a-z]*[.,!;]*[\sA-Za-z]*\$\s*" + str(fee) + "\.*\d*\s*[A-Za-z\s,'()\$\d]*[.!]*",
                "\?\s*[A-Za-z.,\s]*\$\s*" + str(fee) + "\.*\d*\s*[A-Za-z\s,']*[.!]*", 
                "\?\s*[A-Za-z.,\s\$\d]*[A-Z]?[a-z]*[.,!?]*\s*[Tt]ermination [Ff]ee\s*[A-Za-z\s,']*[.!]*"]
    for pattern in range(len(patterns)):
        match = re.search(patterns[pattern], txt)
        if match:
            return str(pattern+2) + ": " + match.group().split("Can my price")[0]
    return "N/A"


def getAdditionalFees(txt):
    # assuming the PDf file is empty, 10 is arbitrary
    if len(txt) < 10:
        return "PDF corrupted"

    match = re.findall("[;.!?\n](['’`\dA-Za-z\s,_:\(\);\-\"\$\%]*(?:[Aa]dditional|[Oo]ther|[Rr]ecurring)\s*(?:fees?|charges?)\s*['’`\dA-Za-z\s,_:\(\);\-\"\$\%]+\.)", txt)

    return "not found" if not match else "".join(match)


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

"""
if __name__ == "__main__":
    print(getPDFasText("PDFs/PowerNext-1.pdf"))
"""

if __name__ == "__main__":
    pdfContent = getPDFasText("Terms of Services/SOUTHERN FEDERAL POWER LLC.pdf")
    if len(pdfContent) < 10:
        print("emptyyy", len(pdfContent))
    print(len(pdfContent),"content:",pdfContent, "\n\n")
    fees = getAdditionalFees(pdfContent)
    print(fees)
