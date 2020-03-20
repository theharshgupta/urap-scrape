import csv
from datetime import date
import bs4 as bs

#get's the value of an attribute using a certain offset (described below)
def getValue(string, sub, offset=2):
    start = string.index(sub) + len(sub) + offset 
    #+2 for ="
    #0 if need id="plan
    end = string.index("\"", start)
    return string[start : end]

#get's the number inside the content of a block with a certain attribute value
def getNum(row, attribute, value):
    content = str(row.find(attrs={attribute : value}).contents)
    s = ''.join(x for x in content if x.isdigit()) #gets all numbers within the contents
    if s:
        return int(s)
    else:
        return 0

#fill suppliers with suppliers that have supplier information as instance variables
def fill_suppliers():
    table = soup.find_all('table', class_ = "nice_table responsive highlight_table display nowrap")[0]
    first = True
    planNum = 0
    iterator = iter(table.find_all('tr'))
    next(iterator) #skip first entry, which is a header
    for row in iterator:
        info = {}
        rowString = str(row)
        if row.attrs['style'] == "display: none;":
            continue
        info["TDU_service_territory"] = getValue(rowString, "data-ratetitle")
        if first:
            info["supplier_name"] = info["TDU_service_territory"]
        else:
            info["supplier_name"] = getValue(rowString, "data-friendly-name")
        info["supplier_id"] = getValue(rowString, "id=\"plan-", 0)
        info["incumbent_flag"] = first
        info["plan_order_rank"] = planNum
        mobilerateDiv = row.findAll("div", class_="mobilerate")[1]
        contractTerm = ""
        for elem in mobilerateDiv.find("div", class_="companyShortData").contents:
            if "Billing Cycle" in elem:
                contractTerm += elem.replace("\n", "").strip() + " "
        info["contract_term"] = contractTerm
        info["early_termination_fee"] = getNum(row, "id", "can_value")
        info["enrollment_fee"] = getNum(row, "id", "enroll_value")
        info["percent_renewable"] = getNum(row, "data-th", "RENEWABLE ENERGY")
        info["rate_type"] = getValue(rowString, "data-priceplan")
        info["variable_rate"] = '{:,.2f}¢'.format(getNum(row, "class", "supply_rate")/100)
        info["fixed_charge"] = '${:,.2f}'.format(getNum(row, "id", "recur_value")/100)
        info["additional_incentives"] = row.find("td", class_="col_7").contents[0].replace("\n", "").strip()
        info["enroll_online"] = "Online Enrollment" in rowString
        info["new_customer_only"] = "New Customer" in rowString
        info["estimated_monthly_cost"] = '${:,.2f}'.format(getNum(row, "data-th", "GENERATION SUPPLY COST PER MONTH")/100)
        if first:
            info["estimated_savings"] = "$0.00"
        else:
            info["estimated_savings"] = "$" + getValue(rowString, "data-th=\"MONTHLY SAVINGS OR ADDITIONAL COST\"", 6)
        first = False
        planNum+=1
        suppliers.append(Supplier(info))

def write_to_csv():
    with open("TDU.csv", mode='w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(suppliers[0].info.keys())
        for supplier in suppliers:
            writer.writerow(supplier.info.values())



#store all information as instance variables
class Supplier:
    date_downloaded = ""
    TDU_service_territory = ""
    supplier_name = ""
    supplier_id = ""
    incumbent_flag = False
    plan_order_rank = -1
    contract_term = -1 #in months
    early_termination_fee = -1
    enrollment_fee = -1
    percent_renewable = -1 #percentage
    rate_type = ""
    variable_rate = "" #cost in C/kW
    fixed_charge = "" #in $
    additional_incentives = ""
    enroll_online = False
    new_customer_only = False
    estimated_monthly_cost = -1 #for 750kW
    estimated_savings = -1 #in comparison to incumbent
    info = {}

    def __init__(self, info):
        self.date_downloaded = date.today();
        self.TDU_service_territory = info["TDU_service_territory"]
        self.supplier_name = info["supplier_name"]
        self.supplier_id = info["supplier_id"]
        self.incumbent_flag = info["incumbent_flag"]
        self.plan_order_rank = info["plan_order_rank"]
        self.contract_term = info["contract_term"]
        self.early_termination_fee = info["early_termination_fee"]
        self.enrollment_fee = info["enrollment_fee"]
        self.percent_renewable = info["percent_renewable"]
        self.rate_type = info["rate_type"]
        self.variable_rate = info["variable_rate"]
        self.fixed_charge = info["fixed_charge"]
        self.additional_incentives = info["additional_incentives"]
        self.enroll_online = info["enroll_online"]
        self.new_customer_only = info["new_customer_only"]
        self.estimated_monthly_cost = info["estimated_monthly_cost"]
        self.estimated_savings = info["estimated_savings"]
        self.info = info

with open('out.html') as html:
    soup = bs.BeautifulSoup(html, 'html.parser')

suppliers = []
fill_suppliers()
write_to_csv()