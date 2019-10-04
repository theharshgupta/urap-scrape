from scrape import get_zipcodes
from scrape import driver

zipcodes_ma = get_zipcodes('MA')
zipcodes_ma = list(map(lambda x: '0' + str(x), zipcodes_ma))
print(zipcodes_ma)


def main_scrape(zipcode):
    driver.get('http://www.energyswitchma.gov/#/')

    driver.find_element_by_xpath('/html/body/div[2]/ui-view/home/div[1]/div[1]/div/div[2]/div/fieldset/form/div['
                                 '1]/div/div[2]/label/input').click()
    driver.find_element_by_xpath('/html/body/div[2]/ui-view/home/div[1]/div[1]/div/div[2]/div/fieldset/form/div['
                                 '2]/div/input').send_keys(zipcode)
    driver.find_element_by_xpath('/html/body/div[2]/ui-view/home/div[1]/div[1]/div/div['
                                 '2]/div/fieldset/form/div[2]/div/button').click()



for zipcode in zipcodes_ma:
    main_scrape(zipcode=zipcode)
