import requests
import json


class API:
    zipcodes = None
    url = "http://api.powertochoose.org/api/PowerToChoose/plans?zip_code="
    id_zipcode_map = {}

    def __init__(self, zipcodes):
        self.zipcodes = zipcodes
        self.all_zips()

    def api_data(self, zipcode):
        """
        Gets data and parses it as per PowerToChoose module specifications
        :param zipcode: zipcode of the place
        :return: None
        """

        response = requests.get(self.url + str(zipcode), verify=False)
        # Each data row has an plan_id that should be same to the idKey in the CSV
        data = json.loads(response.text)['data']
        for row in data:
            if row['plan_id'] in self.id_zipcode_map.keys():
                self.id_zipcode_map[row['plan_id']] = self.id_zipcode_map[row['plan_id']] + [zipcode]
            else:
                self.id_zipcode_map[row['plan_id']] = [zipcode]

    def all_zips(self):
        """
        creates API object for all the zipcodes
        :return: None
        """
        for zipcode in self.zipcodes:
            self.api_data(zipcode)

