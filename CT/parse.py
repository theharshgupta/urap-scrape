import bs4 as bs

with open('out.html') as ex:
    soup = bs.BeautifulSoup(ex, 'html.parser')

table = soup.find_all('table', class_ = "nice_table responsive highlight_table display nowrap")
table = table[0]
data_list = []
for row in table.find_all('tr'):
    for cell in row.find_all('td'):
        data_list.append(cell.attrs)
        print(cell.attrs)

#modify data_list into a 2d array so that each element corresponds to an entire row
data_list_modified = [[]]
for i in range(len(data_list)):
    data_list_modified[i / 7][i % 7] =data_list[i]

#parse all the available data so far and return an object with the data
def parse_data(data):
    for i in range(len(data)):
        if data_list['class'] == ['col_0', 'compInfo']:
            supplier_name = data_list['rel']
        elif data_list['class'] == 'col_1':
            variable_rate = data_list['rel']
        elif data_list['class'] == 'col_2':
            rate_type = data_list['rel']
        elif data_list['class'] == 'col_3':
            percent_renewable = data_list['rel']
        elif data_list['class'] == 'col_4':
            estimated_monthly_cost = data_list['rel']
        elif data_list['class'] == 'col_5':
            if 'rel' in data_list.keys():
                estimated_savings = data_list['rel']
            else:
                break
    #missing some data here
    object = Data(TDU_service_territory, supplier_name,supplier_id, contract_term, early_termination_fee,
                  enrollment_fee, percent_renewable, rate_type, variable_rate, fixed_charge, estimated_monthly_cost, estimated_savings)
    return object
for i in range(len(data_list_modified)):
    parse_data(data_list_modified[i])


class Data:
    TDU_service_territory = None
    supplier_name = None
    supplier_id = None
    contract_term = None
    early_termination_fee = None
    enrollment_fee = None
    percent_renewable = None
    rate_type = None
    variable_rate = None
    fixed_charge = None
    enroll_online = None
    date_downloaded = None
    plan_order_rank = None
    additional_incentives = None
    enroll_online = None
    new_customer_only = None
    estimated_monthly_cost = None
    estimated_savings = None
    flag_incumbent = None

    def __init__(self, TDU_service_territory, supplier_name, supplier_id, contract_term, early_termination_fee,
                 enrollment_fee, percent_renewable, rate_type, variable_rate, fixed_charge,  estimated_monthly_cost, estimated_savings):
        self.TDU_service_territory = TDU_service_territory
        self.supplier_name = supplier_name
        self.supplier_id = supplier_id
        self.contract_term = contract_term
        self.early_termination_fee = early_termination_fee
        self.enrollment_fee = enrollment_fee
        self.percent_renewable = percent_renewable
        self.rate_type = rate_type
        self.variable_rate = variable_rate
        self.fixed_charge = fixed_charge
        self.estimated_monthly_cost = estimated_monthly_cost
        self.estimated_savings = self.estimated_savings