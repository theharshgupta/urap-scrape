import PyPDF2, re, os, sys
import scrapeHelper, warnings
import pytesseract 
from PIL import Image 
from pdf2image import convert_from_path
from sys import *
sys.path.append('..')
from email_service import send_email

# regex that is used to capture everything until a sentence ending
# we cannot just use \W to match non-alphabetic characters, because we want to skip: .!?
rest = "['’`,\dA-Za-z\s_:\(\);\-\"\$%\&]*"
# regex used for capturing endings of sentences
ending = "[\.!\?]*"
# regex used for capturing optional decimal point and optional leading numbers after the point
decimal_points = "\.*\d*"

"""
1. add more to the readme
2. add function to run for all zipcodes
3. email notifications
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
        This function is called from getPDFasText function
        returns: the text resulted from running OCR on the pdf
    """
    try:
        # breaks the pdf into pages
        # 500 is the Image quality in DPI (defaults to 200)
        pages = convert_from_path(pdfPath, 500)
    except Exception as e:
        return ""
    # retrieving the pdf file name
    pdfName = pdfPath.split(".pdf")[0]

    image_counter = 1
    for page in pages:
        # the filename that is used to save the page as .jpg file
        filename = pdfName + "_" + str(image_counter) + ".jpg"
        
        # Save the image of the page in system, if it not doesn't already exist
        if not os.path.exists(filename):
            page.save(filename, 'JPEG') 
    
        image_counter += 1
    
    # Iterate from 1 to total number of pages 
    text = ""
    for i in range(1, image_counter): 
        filename = pdfName+"_"+str(i)+".jpg"

        if platform == "win32" or platform == "cygwin":
            # IMPORTANT: this path might vary across different windows machines
            # make sure it matches to the path where tesseract is located
            pytesseract.pytesseract.tesseract_cmd = r'C:\ProgramFiles\Tesseract-OCR\tesseract.exe'

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
        If PyPDF2 fails, then it performs OCR on the pdf
    """
    ocrForce = False
    output = ""

    try:
        # pdfReader is the object created from processing the pdf
        # it contains the pages, which we can use to extract the text
        pdfReader = PyPDF2.PdfFileReader(open(path, 'rb'))
        for i in range(pdfReader.numPages):
            page = pdfReader.getPage(i)
            output += page.extractText()
    except Exception as e:
        print("Error:", e)
        ocrForce = True

    # assuming if length is < 50, then the pdf library failed
    # 50 is just arbitrary
    # so then we try OCR on it
    if (len(output) < 50 or output.isspace()) and ocrEnabled or ocrForce:
        print("PDF reading library failed, running OCR on", path)
        try:
            output = ocr(path)
        except Exception as e:
            print("error when performing OCR", e)
            send_email(path + " was failed to read\nexception text: " + str(e))
    
    # if a word doesn't fit in 1 line, then it is split by a colon and continued on the next line
    # getting rid of that colon
    output = output.replace('-\n', '')
    return " ".join(output.split("\n")) # replace new lines with space


def getTerminationFee(txt, fee):
    """
        extract a termination fee from the PDF
        returns: the extracted termination fee from the PDF
    """

    # assuming the PDf file is empty, 10 is arbitrary
    if len(txt) < 10:
        return "PDF corrupted "

    # sometimes fee is passed in format like "20/month remaining" or "20.00 month remaining"
    # we only want the value 20 in that case
    fee = fee.split(".")[0]
    try:
        # converting string -> int (eg. "123.123" -> 123)
        # we cannot just do int(fee) because then it fails on cases like "123.123"
        fee = int(float(fee))
    except ValueError:
        # if fee is appended with other characters, then this exception is thrown
        # then we extract the number in it
        m = re.search("\d+", fee)
        if m:
            fee = m.group()

    # match the text "termination fee" from the PDF, this is where we will start to search for the fee details
    match = re.search("[Tt]ermination [Ff]ee[.\n\r]*", txt)
    if match:
        match = re.search("[A-Z]?[a-z]*[.,!;]*[\sA-Za-z]*\$\s*" + str(fee) + decimal_points + rest + ending, match.group())
        if match:
            # we stop at the sentence ending, but some PDFs have just the fee amount and nothing else
            # in that case, the regular expression continues to capture the next question
            # many PDFs have "Can my price change during contract pediod?" in common, not separated from the termination fee
            # if it does have it, then we get rid of it
            # if we don't get rid of it, we get some output like "$150.00Can my price change during..."
            return match.group().strip().split("Can my price")[0]
    
    # if we still haven't found the fee details, then use these regular expressions
    patterns = ["[A-Z]?[a-z]*[.,!;]*[\sA-Za-z]*\$\s*" + str(fee) + decimal_points + rest + ending,
                "\?\s*[A-Za-z.,\s]*\$\s*" + str(fee) + decimal_points + rest + ending, 
                "\?\s*[A-Za-z.,\s\$\d]*[A-Z]?[a-z]*[.,!?]*\s*[Tt]ermination [Ff]ee.*"]
    for pattern in patterns:
        match = re.search(pattern, txt)
        if match:
            # doing the same splitting here also
            return match.group().strip().split("Can my price")[0]
    return " "


def getAdditionalFees(txt):
    """
        Search for additional fees from the text of the PDF
        returns: extracted add-on fees from the PDF
    """
    # assuming the PDf file is empty, 10 is arbitrary
    if len(txt) < 10:
        return "PDF corrupted "
    # starts capturing at the beginning of the sentence and ends at the sentence containing any of the key words
    match = re.findall("[;.!?\n](" + rest + "(?:[Aa]dditional|[Oo]ther|[Rr]ecurring)\s*(?:[Ff]ees?|[Cc]harges?)" + rest + ending + ")", txt)
    return " " if not match else "".join(match)


def getRenewalType(txt):
    """
        Get the renewal details from the text of the PDF
        returns: the renewal details found from the PDF
    """
    # assuming the PDF file is empty, 10 is arbitrary
    if len(txt) < 10:
        return "PDF corrupted "
    # one of the words we look for is "expir", it will match "expire", "expiration", etc.
    # otherwise, the regex is same as the one used in extracting add-on fees
    match = re.findall("[;.!?\n](" + rest + "(?:[Rr]enewal|[Aa]utomatic|[Ee]xpir)" + rest + ending + ")", txt)
    return " " if not match else "".join(match)


def getMinimumUsageFees(txt):
    """
        Uses a regular expression that matches a single sentence containing minimum usage fee
        The regex starts matching beginning at the beginning of the sentence until the end of it
    """
    # assuming the PDF file is empty, 10 is arbitrary
    if len(txt) < 10:
        return "PDF corrupted "
    # in the below regular expression, the reason there's "\.*" is to catch an optional decimal point
    # the regular expression stops matching at the end of the sentence but it needs to catch the decimal point of a dollar amount
    match = re.findall("[;.!?\n](" + rest + "[Mm]inimum" + rest + "[Uu]sage" + rest + "\.*" + rest + ending + ")", txt)
    return " " if not match else "".join(match)

def getBEDCharges(txt):
    """
        Extract the Base, Energy, Delivery Charges from txt
        returns: baseFee, energyFee, deliveryFee
    """
    
    def extractNumber(arr, start):
        """
            Uses a regex to extract a number from a value in arr
        """
        # I decided to only search the next 15 values, because some sentences have "delivery charges", etc.
        # in them, which gives us wrong values because they're just mentioned in sentences
        for j in range(start, start + 15):
            # the reason there's [\dO] is because the OCR sometimes interprets 0 as O
            # and it also sometimes interprets $ as S, so we catch those 
            m = re.search("[\$¢€CS]?\s*[\dO]+\.*\d*\s*[\$¢€]*([Cc]ents?|[Dd]ollars?)*", arr[j])
            if m:
                """
                    Some PDFs have weird spacing and we get ["($)$9.95Energy", "Charge:"] for example
                    In that case, we need to extract $9.95 and return ["energy", "Charge:"],
                    so we can extract the energy charge in the next iteration
                """
                # many PDFs have amount and units (cents) separated, so we check the value at j+1
                out = m.group() + (" cents" if j+1 < len(arr) and ("cents" in arr[j+1].lower()) else "")
                temp = [val for val in ["energy", "delivery", "base"] if val in arr[j].lower()]
                if temp != []:
                    arr[j] = temp[0]
                    return out, arr
                else:
                    return out, arr[:j] + arr[j+1:]
        return "", arr

    # TODO: improve this function to find units beyond just checking its neighbors
    def appendUnit(val, txt, indexOfVal):
        if "$" in val or "¢" in val:
            return val
        elif "$" in txt[indexOfVal + 1] or "¢" in txt[indexOfVal + 1]:
            return val + txt[indexOfVal + 1]
        elif "$" in txt[indexOfVal - 1] or "¢" in txt[indexOfVal - 1]:
            return val + txt[indexOfVal - 1]
        return val

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
        if "base" in txt[i].lower() and base == "" and i+1<len(txt) and "charge" in txt[i+1].lower():
            base, txt = extractNumber(txt, i+1)
        # some companies have "energy" in their company names, so I need to check if the next word is either "charge" or "rate"
        if ("energy" in txt[i].lower() or "supply" in txt[i].lower()) and energy == "" and i+1<len(txt) and ("charge" in txt[i+1].lower() or "rate" in txt[i+1].lower()):
            energy, txt = extractNumber(txt, i+1)
        # some PDFs have "Oncor Electric Delivery", so we have to make sure the next word contains "charge"
        if "delivery" in txt[i].lower() and delivery == "" and i+1<len(txt) and "charge" in txt[i+1].lower():
            delivery, txt = extractNumber(txt, i+1)
    return base, energy, delivery



##################### Test Cases ######################
# feel free to erase them

"""
if __name__ == "__main__":
    all_pdfs = [f for f in os.listdir("PDFs/") if os.path.isfile("PDFs/" + f) and isPDFFile(f)]

    for pdf in all_pdfs:
        txt = getPDFasText("PDFs/" + pdf)
        print(pdf, getTerminationFee(txt), "\n\n")
"""

""" Example 1 of a unreadable PDF """
#txt = getPDFasText("PDFs/WINDROSE ENERGY.pdf")
#print("Length of PDF:", len(txt))
#fee = getTerminationFee(txt, "125")
#print(getMinimumUsageFees(txt))
#print(fee)
"""
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
    print(getBEDCharges(getPDFasText("data/PDFs/Liberty Power.pdf")))
