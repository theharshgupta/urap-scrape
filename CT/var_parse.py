import bs4 as bs
from datetime import date
import csv
import datetime

class Supplier:
    info = {}

    def __init__(self, info):
        self.info = info


with open("./data/" + 'example.html') as html:
    soup = bs.BeautifulSoup(html, 'html.parser')

suppliers = []


def getValue(string, sub, offset=2):
    start = string.index(sub) + len(sub) + offset
    # +2 for ="
    # 0 if need id="plan
    end = string.index("\"", start)
    return string[start: end]


def write_to_csv():
    with open("./data/"+ "PVD_ES.csv", mode='w') as csv_file:
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



def fill_suppliers():
    table = soup.find_all('table', class_ = "nice_table responsive highlight_table display nowrap")[0]
    first = True
    planNum = 0
    iterator = iter(table.find_all('tr'))
    year = datetime.date.today().year - 1
    next(iterator) #skip first entry, which is a header
    for row in iterator:
        counter = 0
        info = {}
        rowString = str(row)
        info["date_downloaded"] = date.today()
        if row.attrs['style'] == "display: none;":
            continue
        service = getValue(rowString, "data-ratetitle")
        info["TDU_service_territory"] = "Eversource" if "Eversource" in service else service
        if first:
            info["supplier_name"] = info["TDU_service_territory"]
        else:
            info["supplier_name"] = getValue(rowString, "data-friendly-name")
        info["plan_id"] = getValue(rowString, "id=\"plan-", 0)
        curr_id = info["plan_id"]
        curr_low = soup.find(id = "low_value_" + curr_id)
        if curr_low and curr_low['value'].find(str(year)) != -1:
            indexes = find_all_indexes(curr_low['value'],str(year))
            indexes_2 = find_all_indexes(curr_low['value'],str(year+1))
            low_list = []
            for i in indexes:
                low_list.append(curr_low['value'][i + 19: i + 23])
            for i in indexes_2:
                low_list.append(curr_low['value'][i + 19: i + 23])
            info["past_low_value"] =  low_list
            curr_high = soup.find(id = "low_value_" + curr_id)['value']
            indexes = find_all_indexes(curr_high,str(year))
            indexes_2 = find_all_indexes(curr_high,str(year+1))
            high_list = []
            for i in indexes:
                high_list.append(curr_high[i + 19: i + 23])
            for i in indexes_2:
                high_list.append(curr_high[i + 19: i + 23])
            info["past_high_value"] =  high_list
            planNum += 1
            first = False
            suppliers.append(Supplier(info))

fill_suppliers()

write_to_csv()