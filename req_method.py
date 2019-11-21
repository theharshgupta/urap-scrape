import requests
import json
import zipcodes
from bs4 import BeautifulSoup


def get_zipcodes(state):
    zipcodes_list_dict = zipcodes.filter_by(state=state)
    return [int(x['zip_code']) for x in zipcodes_list_dict]


def get_distribution_companies(zipcode):
    """
    This function will all the companies for a particular zipcode -- as part of the response
    zipcode: zipcode for MA
    :return: json response
    """
    post_data_1 = dict(customerClassId=1,
                       zipCode=str(zipcode))
    r = requests.post("http://www.energyswitchma.gov/consumers/distributioncompaniesbyzipcode", data=post_data_1)
    jsonify_r = json.loads(r.text)
    return jsonify_r


data = {}


def get_suppliers(zipcode):
    print(zipcode)
    companies_list = []
    companies = {}
    dist_companies_data = get_distribution_companies(zipcode=zipcode)
    data["zipcode"] = zipcode
    for dist_company in dist_companies_data:
        company_id = dist_company['distributionCompanyId']
        company_name = dist_company['distributionCompanyName']
        is_municipal = dist_company['isMunicipalElectricCompany']
        companies["distribution_company"] = company_name
        companies["company_id"] = company_id
        companies["is_municipal"] = is_municipal
        if is_municipal:
            companies["suppliers"] = None
        else:
            post_data = dict(customerClassId="1",
                             distributionCompanyId=str(company_id),
                             distributionCompanyName=str(company_name),
                             monthlyUsage=600,
                             zipCode="02478")
            r2 = requests.post("http://www.energyswitchma.gov/consumers/compare", data=post_data)
            suppliers_list = json.loads(r2.text)
            companies["suppliers"] = suppliers_list
            companies_list.append(companies)
    if len(companies_list) > 0:
        data["companies"] = companies_list
        # print(f"\t {json.dumps(data)}")
        return data

if __name__ == '__main__':
    massachusetts = {}
    zipcodes_ma = get_zipcodes('MA')
    zipcodes_ma = list(map(lambda x: '0' + str(x), zipcodes_ma))
    all_zipcodes_data = []
    for zipcode in zipcodes_ma[:5]:
        datum = get_suppliers(zipcode=str(zipcode))
        all_zipcodes_data.append(datum)
    massachusetts["data"] = all_zipcodes_data
    newjson = json.dumps(massachusetts)
    print(newjson)
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(massachusetts, f)

