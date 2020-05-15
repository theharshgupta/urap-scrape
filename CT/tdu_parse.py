import csv
from datetime import datetime
from datetime import date
import bs4 as bs
from csv_diff import load_csv, compare
import os
import email_error

#get's the value of an attribute using a certain offset (described below)
def getValue(string, attribute, offset=2):
    start = string.index(attribute) + len(attribute) + offset 
    #+2 for ="
    #0 if need id="plan
    end = string.index("\"", start)
    return string[start : end]

#get's the number inside the content of a block with a certain attribute value
def getNum(row, attribute, value):
    try:
        content = str(row.find(attrs={attribute : value}).contents)
    except:
        email_error("No such attribute and value exist. Attribute: " + attribute + " Value: " + value)
    s = ''.join(x for x in content if x.isdigit()) #gets all numbers within the contents
    if s:
        return int(s)
    else:
        return 0

def billingCycle(row):
    try:
        mobilerateDiv = row.findAll("div", class_="mobilerate")[1]
    except:
        email_error("There is no div with value mobilerate.")
    contractTerms = []
    for elem in mobilerateDiv.find("div", class_="companyShortData").contents:
        if "Billing Cycle" in elem:
            contractTerms.append(''.join(x for x in elem if x.isdigit()))
    if len(contractTerms) > 2:
        email_error.send_email("more than two fixed tiers")
    return contractTerms

def varRate(row):
    supplyRates = row.findAll("b", class_="supply_rate")
    if supplyRates == []:
        email_error("Empty array for supply_rate class (no variable rate corresponding to this).")
    rates = []
    for rate in supplyRates:
        stripped = str(rate.contents[0]).replace("\n", "").strip()
        rates.append('{:,.4f}'.format(float(''.join(x for x in stripped if x.isdigit() or x == '.'))/100))
    return rates

#fill suppliers with suppliers that have supplier information as instance variables
def fill_suppliers(suppliers, soup):
    table = soup.find_all('table', class_ = "nice_table responsive highlight_table display nowrap")[0]
    first = True
    planNum = 0
    iterator = iter(table.find_all('tr'))
    next(iterator) #skip first entry, which is a header
    for row in iterator:
        info = {}
        rowString = str(row)
        if row.attrs['style'] == "display: none;": #some elements are hidden
            continue
        info["date_downloaded"] = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        service = getValue(rowString, "data-ratetitle")
        if "Eversource" in service:
            service = "Eversource"
        elif "UI" in service:
            service = "UI"    
        info["TDU_service_territory"] = service
        if first:
            info["supplier_name"] = info["TDU_service_territory"]
        else:
            info["supplier_name"] = getValue(rowString, "data-friendly-name")
        info["plan_id"] = getValue(rowString, "id=\"plan-", 0)
        info["incumbent_flag"] = first
        info["plan_order_rank"] = planNum
        months = billingCycle(row)
        for i in [1,2]:
            key = "contract_term_" + str(i)
            info[key] = months[i-1] if len(months) >= i else ""
        info["early_termination_fee"] = '{:,.2f}'.format(getNum(row, "id", "can_value"))
        assert float(info["early_termination_fee"]) >= 0, "the early_termination_fee should be nonnegative"
        info["enrollment_fee"] = '{:,.2f}'.format(getNum(row, "id", "enroll_value"))
        assert float(info["enrollment_fee"]) >= 0, "the enrollment_fee should be nonnegative"
        renewable = getNum(row, "data-th", "RENEWABLE ENERGY")/100
        assert 0<=renewable<=1, "renewable percentage is not within range: " + str(renewable)
        info["percent_renewable"] = '{:,.2f}'.format(renewable)
        info["rate_type"] = getValue(rowString, "data-priceplan")
        rates = varRate(row)
        for i in [1,2]: #need to see if there are more than 2 tiers max
            key = "variable_rate_" + str(i)
            info[key] = rates[i-1] if len(rates) >= i else ""
        info["fixed_charge"] = '{:,.2f}'.format(getNum(row, "id", "recur_value")/100)
        assert float(info["fixed_charge"]) >= 0, "the fixed_charge should be nonnegative"
        addInfo = row.find("td", class_="col_7").contents;
        info["additional_incentives"] = addInfo[0].replace("\n", "").strip() if len(addInfo) != 0 else "";
        info["enroll_online"] = "Online Enrollment" in rowString
        info["new_customer_only"] = "New Customer" in rowString
        info["estimated_monthly_cost"] = '{:,.2f}'.format(getNum(row, "data-th", "GENERATION SUPPLY COST PER MONTH")/100)
        assert float(info["estimated_monthly_cost"]) >= 0, "the estimated_monthly_cost should be nonnegative"
        if first:
            info["estimated_savings"] = "0.00"
        else:
            info["estimated_savings"] = '{:,.2f}'.format(float(getValue(rowString, "data-th=\"MONTHLY SAVINGS OR ADDITIONAL COST\"", 6)))
        first = False
        planNum+=1
        suppliers.append(Supplier(info))
    

#writes all info into a csv
def write_to_csv(supplier, suppliers):
    dateStr = str(datetime.now().strftime("%m_%d_%Y_%H:%M"))
    with open("./data/TDU_" + supplier + "_" + dateStr + ".csv", mode='w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(suppliers[0].info.keys())
        for s in suppliers:
            writer.writerow(s.info.values())
    diff_check(supplier)

#deletes if there is no variation in plan_id from the last csv from the same supplier
def diff_check(supplier):
    files = sorted([x for x in os.listdir("./data/") if x.endswith(".csv")], key=lambda x: os.path.getmtime("./data/" + x), reverse=True)
    if len(files) < 2:
        email_error.send_email("not enough files to compare")
        return
    for i in range(len(files)):
        if supplier in str(files[i]):
            now = files[i]
            for j in range(i+1, len(files)):
                if supplier in str(files[j]):
                    recent = files[j]
                    break
            break
    diff = compare(load_csv(open("./data/" + now), key="plan_id"), load_csv(open("./data/" + recent), key="plan_id"))
    if diff['added'] == [] or diff['removed'] == []:
        os.remove("./data/" + now)
        print('deleted')


#store all information in a dictionary
class Supplier:
    info = {}
    def __init__(self, info):
        self.info = info

def run(supplier):
    try:
        with open("./data/" + supplier + '.html') as html:
            soup = bs.BeautifulSoup(html, 'html.parser')
        suppliers = []
        fill_suppliers(suppliers, soup)
        write_to_csv(supplier, suppliers)
    except Exception as e:
        print("error encountered: " + str(e))
        email_error.send_email("general error: " + str(e))