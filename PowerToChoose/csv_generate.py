from scrapeHelper import *
from pdfReader import *
import sys

from PowerToChoose.pdfReader import getPDFasText, getTerminationFee
from PowerToChoose.scrapeHelper import getCurrentDate

sys.path.append('..')
from email_service import send_email


def generateCSVTemplate(fileNameWithExtension, mode):
    """
        this function writes 
    """
    file = open(fileNameWithExtension, mode)
    # these are the fields that we will fill
    # make sure to not change the order
    # if you change the order, make sure to change the corresponding write call in writeToCSV function
    file.write("\nDate Downloaded,State,TDU Service Territory,Zip,Supplier Name," +
               "Plan Name,Variable Rate 500kWh,Variable Rate 1000kWh,Variable Rate 2000kWh," +
               "Rate Type,Contract Term,Cancellation Fee,Termination Fee Details,Percent Renewable," +
               "Fact Sheet Name,Terms of Services Name,URL,Fact Sheet,Terms of Service,Enroll Phone," +
               "Additional Fees,Minimum Usage Fee,Renewal Details,Base Charge,Energy Charge,Delivery Charge, Company Rating")
    return file


def writeToCSV(csv, data, fact_sheet_paths):
    """
        given a JSON object containing the data,
        write the data to the csv file
    """

    def write(txt):
        txt = str(txt).replace(",", "")
        txt = str(txt).replace("\n", " ")
        csv.write(str(txt) + ",")

    # make sure to not change the order of the write() calls below
    write(getCurrentDate())
    write("TX")
    write(data["company_tdu_name"])
    write(data["zip_code"])
    write(data["company_name"])
    write(data["plan_name"])
    write(str(data["price_kwh500"]) + " cents")
    write(str(data["price_kwh1000"]) + " cents")
    write(str(data["price_kwh2000"]) + " cents")
    write(data["rate_type"])
    write(str(data["term_value"]) + " months")
    write("$" + data["pricing_details"].split("$")[1])

    pdfContent = getPDFasText(fact_sheet_paths[data["fact_sheet"]])
    termination_fee = getTerminationFee(pdfContent, data["pricing_details"].split("$")[1])
    write(termination_fee)
    write(str(data["renewable_energy_id"]) + "%")
    write(fact_sheet_paths[data["fact_sheet"]])
    write(terms_of_service_paths[data["terms_of_service"]])
    write(data["go_to_plan"])
    write(data["fact_sheet"])
    write(data["terms_of_service"])
    write(data["enroll_phone"])

    terms_of_service_content = getPDFasText(terms_of_service_paths[data["terms_of_service"]])
    write(getAdditionalFees(terms_of_service_content) + getAdditionalFees(pdfContent))
    write(getMinimumUsageFees(terms_of_service_content) + getMinimumUsageFees(pdfContent))
    write(getRenewalType(terms_of_service_content) + getRenewalType(pdfContent))

    base, energy, delivery = getBEDCharges(pdfContent)
    write(base)
    write(energy)
    write(delivery)
    write(data["rating_total"])


# when downloading a PDF, sometimes 2 plans from the same company end up overriding each other
# and we end up with 1 pdf file, so we will save them with different names and store them here
fact_sheet_paths = {}
terms_of_service_paths = {}

if __name__ == "__main__":
    zip_code = 75001 if len(sys.argv) <= 1 else sys.argv[1]
    json = getJSON(zip_code)
    sample_count = len(json["data"]) if len(sys.argv) < 2 else int(sys.argv[2])

    if sample_count > len(json["data"]):
        sample_count = len(json["data"])

    if sample_count == 0:
        print("No plan exist for this zip code", zip_code)
        sys.exit(0)

    if json["success"]:
        file = generateCSVTemplate(str(zip_code) + ".csv", "w+")
        for i in range(sample_count):
            plan = json["data"][i]

            # downloadPDf returns the file name of the saved pdf file
            fact_sheet_paths[plan["fact_sheet"]] = downloadPDF(getEmbeddedPDFLink(plan["fact_sheet"]),
                                                               plan["company_name"], "PDFs/")
            terms_of_service_paths[plan["terms_of_service"]] = downloadPDF(getEmbeddedPDFLink(plan["terms_of_service"]),
                                                                           plan["company_name"], "Terms of Services/")
            file.write("\n")
            writeToCSV(file, plan, fact_sheet_paths)
    else:
        send_email("API failure")
        print("API response fail")
