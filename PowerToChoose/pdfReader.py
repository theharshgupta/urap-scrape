import PyPDF2, re, os, sys
import scrapeHelper, warnings
import pytesseract 
from PIL import Image 
from pdf2image import convert_from_path

rest = "['’`\dA-Za-z\s,_:\(\);\-\"\$\%]*"
ending = "[.!]"
decimal_points = "\.*\d*"

# by doing this, warnings will be treated as errors
# we do this to catch PdfReadWarning
#warnings.filterwarnings("error")

"""
1. company rating (one pass through powertochoose.com)
3. email notifications
4. combine energy, base, delivery charges into 1 function
5. bill credit (with usage range)
6. usage charge (with usage range)
7. figure out a way how to capture ranges in charges/fees
8. figure out how to work it on a windows machine
"""

def isPDFFile(fileName):
    """
        checks whether fileName is a pdf file
        fileName is a PDF file, if the extension is .pdf
    """
    return len(fileName) >= 4 and fileName[-4:] == ".pdf"


def ocr(pdfPath):
    """
        Perform OCR on a PDF given by pdfPath
    """
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

        # Recognize the text as string in image using pytesseract
        text += str(((pytesseract.image_to_string(Image.open(filename))))) 
    return text
    

def getPDFasText(path, ocrEnabled=True):
    """
        path: must be in the format parentFolder + fileName + extension
        example of valid paths:
            1) PDFs/AMBIT ENERGY.pdf
            2) PDFs/Energy to Go.pdf

        returns: The text representation of the given PDF file

        It reads the PDF file using PyPDF2 library and gets the PDF file as a string
    """
    ocrForce = False
    output = ""
    try:
        pdfReader = PyPDF2.PdfFileReader(open(path, 'rb'))
        for i in range(pdfReader.numPages):
            page = pdfReader.getPage(i)
            output += page.extractText()
    except Exception as e:
        print("Error:", e)
        ocrForce = True
    # assuming if length is < 50, then the pdf library failed
    # so then we try OCR on it
    if len(output) < 50 and ocrEnabled or ocrForce:
        print("PDF library most likely failed, running OCR on", path)
        try:
            output = ocr(path)
        except Image.DecompressionBombError:
            print("error")
    
    output = output.replace('-\n', '')
    return " ".join(output.split("\n")) # replace new lines with space


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

    # match the text "termination fee" from the PDF, this is where we will start to search for the fee details
    match = re.search("[Tt]ermination [Ff]ee[\W\w\d\n\r\s]*", txt)
    if match:
        match = re.search("[A-Z]?[a-z]*[.,!;]*[\sA-Za-z]*\$\s*" + str(fee) + decimal_points + rest + ending, match.group())
        if match:
            # many PDFs have "Can my price change during contract pediod?" in common, not separated from the termination fee
            # if it does have it, then we get rid of it
            return match.group().strip().split("Can my price")[0]
    
    # if we still haven't found the details, then use these regular expressions
    patterns = ["[A-Z]?[a-z]*[.,!;]*[\sA-Za-z]*\$\s*" + str(fee) + decimal_points + rest + ending,
                "\?\s*[A-Za-z.,\s]*\$\s*" + str(fee) + decimal_points + rest + ending, 
                "\?\s*[A-Za-z.,\s\$\d]*[A-Z]?[a-z]*[.,!?]*\s*[Tt]ermination [Ff]ee.*"]
    for pattern in patterns:
        match = re.search(pattern, txt)
        if match:
            return match.group().strip().split("Can my price")[0]
    return " "


def getAdditionalFees(txt):
    """
        Search for additional fees from the text of the PDF
    """
    # assuming the PDf file is empty, 10 is arbitrary
    if len(txt) < 10:
        return "PDF corrupted"
    match = re.findall("[;.!?\n](" + rest + "(?:[Aa]dditional|[Oo]ther|[Rr]ecurring)\s*(?:fees?|charges?)" + rest + ending + ")", txt)
    return " " if not match else "".join(match)


def getRenewalType(txt):
    """
        Get the renewal details from the text of the PDF
    """
    # assuming the PDf file is empty, 10 is arbitrary
    if len(txt) < 10:
        return "PDF corrupted"
    match = re.findall("[;.!?\n](" + rest + "(?:[Rr]enewal|[Aa]utomatic|[Ee]xpir)" + rest + ending + ")", txt)
    return " " if not match else "".join(match)


def getMinimumUsageFees(txt):
    # assuming the PDF file is empty, 10 is arbitrary
    if len(txt) < 10:
        return "PDF corrupted"
    match = re.findall("[;.!?\n](" + rest + "[Mm]inimum" + rest + "[Uu]sage" + rest + ending + ")", txt)
    return " " if not match else "".join(match)

def getBaseCharge(txt):
    # assuming the PDF file is empty, 10 is arbitrary
    if len(txt) < 10:
        return "PDF corrupted"
    match = re.findall("[;.!?\n]*(" + rest + "[Bb]ase\s*[Cc]harge" + ".+" + ")", txt)
    print(re.findall("[Bb]ase\s*[Cc]harge" + rest, txt))
    return " " if not match else "".join(match)

def getEnergyCharge(txt):
    # assuming the PDF file is empty, 10 is arbitrary
    if len(txt) < 10:
        return "PDF corrupted"
    match = re.findall("[;.!?\n]*(" + rest + "[Ee]nergy\s*[Cc]harge" + ".+" + ")", txt)
    return " " if not match else "".join(match)

def getDeliveryCharge(txt):
    # assuming the PDF file is empty, 10 is arbitrary
    if len(txt) < 10:
        return "PDF corrupted"
    match = re.findall("[;.!?\n]*(" + rest + "[Dd]elivery\s*[Cc]harge" + ".+" + ")", txt)
    return " " if not match else "".join(match)

def getBEDCharges(txt):
    """
        Extract the Base, Energy, Delivery Charges from txt
    """

    def isValidUnitValue(unit, word):
        # TODO: documentation
        for item in word.split(unit):
            try:
                float(item) # if this works without exception, then we return
                return True
            except Exception:
                pass
    
    def extractNumber(arr, start):
        # TODO: documentation here
        for j in range(start, len(arr)):
            if isValidUnitValue("$", arr[j]):
                return arr[j], arr[:j] + arr[j+1:]
            elif isValidUnitValue("¢", arr[j]):
                return arr[j], arr[:j] + arr[j+1:]
        return "", arr

    base, energy, delivery = "", "", ""

    # This is to shorten the length of text we need to process
    # Reading the whole text might fail on large texts when we run split()
    # TODO: fix this
    # txt = "".join(re.findall("[Bb]ase\s*[Cc]harge\s*.{5,500}", txt))
    txt = txt.split(" ")
    for i in range(len(txt)):
        # we update txt sometimes each iteration, so this check is necessary
        if i >= len(txt):
            break
        if txt[i].lower() == "base":
            print(txt)
            base, txt = extractNumber(txt, i+1)
        # some companies have "energy" in their company names, so I need to check if the next word is either "charge" or "rate"
        elif txt[i].lower() == "energy" and i+1<len(txt) and (txt[i+1].lower() == "charge" or txt[i+1].lower() == "rate"):
            energy, txt = extractNumber(txt, i+1)
        elif txt[i].lower() == "delivery":
            delivery, txt = extractNumber(txt, i+1)
    return base, energy, delivery


            

##################### Test Cases ######################

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
    """
    pdfContent = getPDFasText("Terms of Services/GREEN MOUNTAIN ENERGY COMPANY-1.pdf")
    if len(pdfContent) < 10:
        print("emptyyy", len(pdfContent))
    #print(len(pdfContent),"content:",pdfContent, "\n\n")
    fees = getRenewalType(pdfContent)
    print(getMinimumUsageFees(pdfContent))
    print(fees)
    """
    #print(getTerminationFee("faw;klfjelfkjwalkf\nfejflwekfj\ntermination fee is $50 now you know.\n helloworld fefjaewfklaj\n fefaewfaef\n", "50"))
    #print(getBaseCharge("This price disclosure is based on the following components:\nBase Charge: Energy Charge: Oncor Electric Delivery Charges:\n$5.00 per billing cycle 7.9842¢ per kWh"))
    #print(getBEDCharges("Base Charge Energy Delivery $5 10$ 15¢"))
    #print(getBEDCharges("Base charge $5 Energy $10 Delivery 0.038447"))

    # it fails here, they have Energy Charge:3.0¢, so use regular expressions instead of split()
    print(getBEDCharges(getPDFasText("PDFs/CHAMPION ENERGY SERVICES LLC.pdf")))