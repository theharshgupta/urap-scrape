from datetime import date
import bs4 as bs

def getValue(string, sub, offset=2):
    start = string.index(sub) + len(sub) + offset 
    #+2 for ="
    #0 if need id="plan
    end = string.index("\"", start)
    return string[start : end]

def getNum(row, attribute, value):
    content = str(row.find(attrs={attribute : value}).contents)
    s = ''.join(x for x in content if x.isdigit()) #gets all numbers within the contents
    if s:
        return int(s)
    else:
        return 0

with open('out.html') as html:
    soup = bs.BeautifulSoup(html, 'html.parser')

table = soup.find_all('table', class_ = "nice_table responsive highlight_table display nowrap")[0]
first = True
planNum = 0
iterator = iter(table.find_all('tr'))
next(iterator) #skip first entry, which is a header
for row in iterator:
    values = {}
    rowString = str(row)
    if row.attrs['style'] == "display: none;":
        continue
    values["TDU_service_territory"] = getValue(rowString, "data-ratetitle")
    if first:
        values["supplier_name"] = values["TDU_service_territory"]
    else:
        values["supplier_name"] = getValue(rowString, "data-friendly-name")
    values["supplier_id"] = getValue(rowString, "id=\"plan-", 0)
    values["incumbent_flag"] = first
    values["plan_order_rank"] = planNum
    # values["contract_term"]
    values["early_termination_fee"] = getNum(row, "id", "can_value")
    values["enrollment_fee"] = getNum(row, "id", "enroll_value")
    values["percent_renewable"] = getNum(row, "data-th", "RENEWABLE ENERGY")
    values["rate_type"] = getValue(rowString, "data-priceplan")
    values["variable_rate"] = '{:,.2f}¢'.format(getNum(row, "class", "supply_rate")/100)
    values["fixed_charge"] = '${:,.2f}'.format(getNum(row, "id", "recur_value")/100)
    # values["additional_incentives"]
    values["enroll_online"] = "Online Enrollment" in rowString
    values["new_customer_only"] = "New Customer" in rowString
    values["estimated_monthly_cost"] = '${:,.2f}'.format(getNum(row, "data-th", "GENERATION SUPPLY COST PER MONTH")/100)
    if first:
        values["estimated_savings"] = "$0.00"
    else:
        values["estimated_savings"] = "$" + getValue(rowString, "data-th=\"MONTHLY SAVINGS OR ADDITIONAL COST\"", 6)
    first = False
    planNum+=1



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

    def __init__(self, values):
        self.date_downloaded = date.today();
        self.TDU_service_territory = values["TDU_service_territory"]
        self.supplier_name = values["supplier_name"]
        self.supplier_id = values["supplier_id"]
        self.incumbent_flag = values["incumbent_flag"]
        self.plan_order_rank = values["plan_order_rank"]
        self.contract_term = values["contract_term"]
        self.early_termination_fee = values["early_termination_fee"]
        self.enrollment_fee = values["enrollment_fee"]
        self.percent_renewable = values["percent_renewable"]
        self.rate_type = values["rate_type"]
        self.variable_rate = values["variable_rate"]
        self.fixed_charge = values["fixed_charge"]
        self.additional_incentives = values["additional_incentives"]
        self.enroll_online = values["enroll_online"]
        self.new_customer_only = values["new_customer_only"]
        self.estimated_monthly_cost = values["estimated_monthly_cost"]
        self.estimated_savings = values["estimated_savings"]