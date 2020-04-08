import bs4 as bs
from datetime import date
import csv


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



def fill_suppliers():
    table = soup.find_all('table', class_ = "nice_table responsive highlight_table display nowrap")[0]
    first = True
    planNum = 0
    iterator = iter(table.find_all('tr'))
    next(iterator) #skip first entry, which is a header
    for row in iterator:
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
        if soup.find(id = "low_value_" + curr_id):
            info["past_low_value"] =  soup.find(id = "low_value_" + curr_id)
            info["past_high_value"] =  soup.find(id = "high_value_" + curr_id)
            planNum += 1
            first = False
            suppliers.append(Supplier(info))

fill_suppliers()
write_to_csv()

