from scrapeHelper import *
from pdfReader import *
import sys

def generateCSVTemplate(fileNameWithExtension):
    file = open(fileNameWithExtension, "w+")
    file.write("Date Downloaded,State,TDU Service Territory,Zip,Supplier Name," +
        "Plan Name,Variable Rate 500kWh,Variable Rate 1000kWh,Variable Rate 2000kWh," +
        "Rate Type,Contract Term,Cancellation Fee,Termination Fee Details,Percent Renewable,Renewable Description," +
        "URL,Fact Sheet,Terms of Service")
        #"TDU_Charges_Incl,TDU_Fixed_Charge,TDU_Variable_Charge,Low_Usage_Fee," +
        #"Low_Usage_Fee_Cutoff,Usage_Bill_Credit1,Usage_Bill_Credit1_Cutoff_L,Usage_Bill_Credit1_Cutoff_H," +
        #"Usage_Bill_Credit2,Usage_Bill_Credit2_Cutoff_L,Usage_Bill_Credit2_Cutoff_H," +
        #"Early_Termination_Fee,Early_Termination_Fee_Type,Automatic_Renewal,Percent_Renewable,Renewable_Certification," +
        #"Renewable_Description,Other_Fees,Price_Lag1,Price_Lag2,Price_Lag3," +
        #"Price_Lag4,Price_Lag5,Price_Lag6,Price_Lag7,Price_Lag8,Complaints_Tot_Lag1,Complaints_Tot_Lag2,Complaints_Tot_Lag3," +
        #"Complaints_Tot_Lag4,Complaints_Tot_Lag5,Complaints_Tot_Lag6,Complaints_Billing_Lag1,Complaints_Billing_Lag2," +
        #"Complaints_Billing_Lag3,Complaints_Billing_Lag4,Complaints_Billing_Lag5,Complaints_Billing_Lag6,Complaints_Cramming_Lag1," +
        #"Complaints_Cramming_Lag2,Complaints_Cramming_Lag3,Complaints_Cramming_Lag4,Complaints_Cramming_Lag5,Complaints_Cramming_Lag6," +
        #"Complaints_Discont_Lag1,Complaints_Discont_Lag2,Complaints_Discont_Lag3,Complaints_Discont_Lag4,Complaints_Discont_Lag5," +
        #"Complaints_Discont_Lag6,Supplier_Stars,Intro_Price,Intro_Time_Period,Incentives_Special_Terms,Pre_Pay,Purchase_DG,Plan_Updated")
    return file

def writeToCSV(csv, data, fact_sheet_paths):
    """
    given a JSON object containing the data,
    write the data to the csv file
    """

    def write(txt):
        txt = str(txt).replace(",", "")
        csv.write(str(txt) + ",")

    write(getCurrentDate())
    write("TX")
    write(data["company_tdu_name"])
    write(data["zip_code"])
    write(data["company_name"])
    write(data["plan_name"])
    write(data["price_kwh500"])
    write(data["price_kwh1000"])
    write(data["price_kwh2000"])
    write(data["rate_type"])
    write(str(data["term_value"]) + " months")
    write("$" + data["pricing_details"].split("$")[1])
    print("Reading,", fact_sheet_paths[data["fact_sheet"]], "\n") 
    write(getTerminationFee(getPDFasText(fact_sheet_paths[data["fact_sheet"]]), data["pricing_details"].split("$")[1]))
    write(str(data["renewable_energy_id"]) + "%")
    write(data["renewable_energy_description"])
    write(data["go_to_plan"])
    write(data["fact_sheet"])
    write(data["terms_of_service"])


zip_code = 75001 if len(sys.argv) <= 1 else sys.argv[1]
json = getJsonFromZIP(zip_code)
sample_count = len(json["data"]) if len(sys.argv) < 2 else int(sys.argv[2])

if sample_count > len(json["data"]):
    sample_count = len(json["data"])

# when downloading a PDF, sometimes 2 plans from the same company end up overriding each other
# and we end up with 1 pdf file, so we will save them with different names and store them here
fact_sheet_paths = {}

if json["success"]:
    file = generateCSVTemplate("powertochoose.csv")
    for i in range(sample_count):
        plan = json["data"][i]

        # downloadPDf returns the file name of the saved pdf file
        fact_sheet_paths[plan["fact_sheet"]] = downloadPDF(plan["fact_sheet"], plan["company_name"], "PDFs/")
        file.write("\n")
        writeToCSV(file, plan, fact_sheet_paths)
else:
    print("API response fail")
