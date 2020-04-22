import bs4 as bs
from datetime import date
import csv
import datetime

class Supplier:
    info = {}

    def __init__(self, info):
        self.info = info





def getValue(string, sub, offset=2):
    start = string.index(sub) + len(sub) + offset
    # +2 for ="
    # 0 if need id="plan
    end = string.index("\"", start)
    return string[start: end]


def write_to_csv(supplier, suppliers):
    with open("./data/"+ "PVD_" + supplier +"_"+ str(datetime.date.today()) + ".csv", mode='w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(suppliers[0].info.keys())
        for supplier in suppliers:
            writer.writerow(supplier.info.values())

def find_all_indexes(input_str, search_str):
    l1 = []
    length = len(input_str)
    index = 0
    while index < length:
        i = input_str.find(search_str, index)
        if i == -1:
            return l1
        l1.append(i)
        index = i + 1
    return l1


def fill_suppliers(soup, suppliers):
    table = soup.find_all('table', class_ = "nice_table responsive highlight_table display nowrap")[0]
    first = True
    planNum = 0
    iterator = iter(table.find_all('tr'))
    year = datetime.date.today().year - 1
    duplicate = []
    next(iterator) #skip first entry, which is a header
    for row in iterator:
        counter = 0
        info = {}
        rowString = str(row)
        info["date_downloaded"] = date.today()
        if row.attrs['style'] == "display: none;":
            continue
        service = getValue(rowString, "data-ratetitle")
        if "Eversource" in service:
            service = "Eversource"
        elif "UI" in service:
            service = "UI"
        info["TDU_service_territory"] = service
        if first:
            info["supplier_name"] = info["TDU_service_territory"]
        elif getValue(rowString, "data-friendly-name") in duplicate:
            print(getValue(rowString, "data-friendly-name"))
            continue
        else:
            duplicate.append(getValue(rowString, "data-friendly-name"))
            info["supplier_name"] = getValue(rowString, "data-friendly-name")
        info["plan_id"] = getValue(rowString, "id=\"plan-", 0)
        curr_id = info["plan_id"]
        curr_low = soup.find(id = "low_value_" + curr_id)
        if curr_low and curr_low['value'].find(str(year)) != -1:
            print("1")
            indexes = find_all_indexes(curr_low['value'],str(year))
            indexes_2 = find_all_indexes(curr_low['value'],str(year+1))
            low_list = []
            for i in indexes:
                low_list.append(float(curr_low['value'][i + 19: i + 23]) / 100)
            for i in indexes_2:
                low_list.append(float(curr_low['value'][i + 19: i + 23]) / 100)
            if len(low_list) > 12:
                low_list = low_list[-12:]
            while len(low_list) < 12:
                low_list.append('N/A')
            curr_high = soup.find(id = "high_value_" + curr_id)['value']
            indexes = find_all_indexes(curr_high,str(year))
            indexes_2 = find_all_indexes(curr_high,str(year+1))
            high_list = []
            for i in indexes:
                high_list.append(float(curr_high[i + 19: i + 23]) / 100)
            for i in indexes_2:
                high_list.append(float(curr_high[i + 19: i + 23]) / 100)
            if len(high_list) > 12:
                high_list = high_list[-12:]
            while len(high_list) < 12:
                high_list.append('N/A')
            for i in range(12):
                info["Low_lag" + str(i + 1)] = low_list[11 - i]
                info["High_lag" + str(i + 1)] = high_list[11 - i]
            planNum += 1
            first = False
            if 0 not in low_list :
                suppliers.append(Supplier(info))

def run(supplier):
    with open("./data/" + "ES_PVD.html") as html:
        soup = bs.BeautifulSoup(html, 'html.parser')
    suppliers = []
    fill_suppliers(soup, suppliers)
    write_to_csv(supplier, suppliers)