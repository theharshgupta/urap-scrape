import requests
import json
import zipcodes
import pandas as pd
import os
from pathlib import Path
from datetime import datetime
import glob

ma_zipcodes = [2351, 2018, 1718, 1719, 1720, 2743, 2745, 1220, 2344, 1001, 1230, 1266, 1201, 1653, 2134, 1913, 1002,
               1003, 1004, 1059, 1810, 1812, 1899, 5501, 5544, 2535, 2474, 2475, 2476, 2475, 1430, 1431, 1330, 1721,
               1222, 2339, 2702, 1331, 2703, 2763, 1501, 2466, 2322, 1432, 1434, 2457, 1436, 2212, 1370, 2630, 1005,
               2664, 1062, 1115, 1199, 2151, 1223, 1223, 1730, 1731, 1007, 2019, 2478, 2479, 2779, 1224, 1230, 1503,
               1337, 1915, 1915, 1029, 1821, 1822, 1504, 1008, 1364, 1740, 1009, 2108, 2109, 2110, 2111, 2112, 2113,
               2114, 2115, 2116, 2117, 2118, 2119, 2120, 2121, 2122, 2123, 2124, 2125, 2126, 2127, 2128, 2129, 2130,
               2131, 2132, 2133, 2134, 2135, 2136, 2137, 2163, 2196, 2199, 2201, 2203, 2204, 2205, 2206, 2210, 2211,
               2212, 2215, 2217, 2222, 2228, 2241, 2266, 2283, 2284, 2293, 2297, 2298, 2201, 2467, 2266, 2215, 2532,
               2559, 1719, 1719, 1921, 1505, 1835, 2184, 2185, 2184, 2020, 2631, 2324, 2325, 2325, 2135, 1107, 1010,
               2301, 2302, 2303, 2304, 2305, 1506, 2445, 2446, 2447, 2467, 2447, 2327, 1338, 1803, 1805, 2532, 2542,
               1922, 2138, 2139, 2140, 2141, 2142, 2163, 2238, 2139, 2021, 1741, 2330, 2297, 2534, 2360, 2632, 2634,
               1546, 2783, 2539, 1339, 1346, 2129, 1507, 1508, 1509, 1509, 2712, 2633, 1824, 2150, 2493, 1611, 1225,
               1011, 1012, 2467, 1013, 1014, 1020, 1021, 1022, 2535, 1247, 1510, 1778, 2025, 1253, 1340, 1742, 1341,
               2635, 1050, 2637, 1026, 1002, 2713, 1226, 1227, 1923, 2714, 2747, 2748, 2026, 2027, 1342, 2638, 2639,
               2639, 1432, 1434, 2715, 2121, 2122, 2124, 2125, 2124, 1516, 2030, 1826, 1343, 1571, 1570, 1827, 2331,
               2332, 2536, 1364, 2474, 1504, 2128, 2228, 2184, 2333, 1010, 1515, 2141, 2355, 1370, 1342, 2641, 1516,
               2536, 2717, 1027, 2645, 1054, 1028, 1116, 1904, 1527, 2186, 2643, 1029, 2359, 1463, 1517, 2537, 2143,
               2718, 1438, 2032, 2538, 2472, 2189, 1270, 2642, 1027, 2334, 2539, 1545, 1230, 2337, 1344, 1929, 2149,
               2719, 2720, 2721, 2722, 2723, 2724, 2540, 2541, 2543, 1344, 1745, 1030, 2293, 2477, 1518, 1521, 1420,
               2241, 1062, 1247, 2644, 1886, 1432, 2035, 2035, 1701, 1702, 1703, 1704, 1705, 1701, 1701, 2038, 1440,
               2535, 1833, 1031, 1354, 1229, 1550, 1930, 1931, 1032, 1519, 1033, 1034, 1034, 1230, 2041, 2040, 1606,
               1301, 1302, 1450, 1470, 1471, 2121, 1834, 1230, 1035, 2338, 1521, 1040, 1041, 1936, 1036, 1036, 1237,
               2339, 2340, 1731, 2341, 2645, 1037, 1082, 1230, 1451, 2238, 2645, 2646, 2646, 1519, 2493, 2536, 1038,
               1937, 1830, 1831, 1832, 1833, 1835, 1339, 1039, 1346, 2018, 2043, 2044, 1235, 1050, 2343, 1520, 1521,
               1746, 1040, 1041, 1367, 1747, 1748, 2790, 2169, 1236, 1452, 1749, 2045, 2047, 1050, 2601, 2647, 2126,
               2136, 2137, 1151, 1151, 2139, 1266, 1812, 5501, 5544, 1938, 2090, 2130, 1522, 2217, 1824, 2493, 2142,
               2215, 2364, 1050, 1805, 1364, 1347, 2347, 2348, 1562, 1523, 1224, 1237, 1237, 1840, 1841, 1842, 1843,
               1238, 1264, 1053, 1524, 1240, 1242, 1453, 1054, 2420, 2421, 1301, 1337, 1773, 1773, 1525, 1032, 1460,
               1106, 1116, 1027, 1850, 1851, 1852, 1853, 1854, 1056, 1462, 1901, 1902, 1903, 1904, 1905, 1910, 1940,
               1930, 2148, 1526, 1944, 1944, 2345, 2048, 1945, 1263, 2171, 2738, 1263, 1752, 1752, 2050, 2065, 2051,
               2648, 2649, 1111, 2204, 1889, 2204, 2126, 2739, 1754, 2052, 2153, 2155, 2156, 2053, 1813, 2176, 1756,
               2552, 1860, 1844, 1945, 2344, 2346, 2348, 2349, 2344, 2346, 2348, 2349, 1243, 1949, 1757, 1244, 1527,
               1586, 1349, 1504, 2054, 1529, 2186, 2187, 2055, 2120, 2350, 1350, 1350, 1057, 1351, 1245, 1050, 1085,
               2553, 1505, 1354, 1027, 1258, 1354, 1258, 1886, 1908, 2045, 2554, 2564, 2584, 1760, 2492, 2494, 2494,
               2492, 1237, 2740, 2741, 2742, 2743, 2744, 2745, 2746, 1531, 1470, 1471, 1230, 1230, 1230, 1355, 1364,
               2649, 2456, 1922, 1951, 1950, 1951, 2456, 2458, 2459, 2460, 2461, 2462, 2464, 2465, 2466, 2467, 2468,
               2495, 2459, 2459, 2461, 2462, 2464, 2458, 2460, 2462, 1247, 2760, 2356, 1252, 1360, 1536, 1066, 1760,
               2171, 2495, 2748, 2056, 2171, 2351, 1247, 1059, 1845, 2760, 2761, 2762, 2763, 1862, 1535, 2140, 2355,
               2650, 1863, 1050, 2747, 2764, 2651, 2356, 2357, 1230, 1252, 2556, 2565, 1360, 1536, 1035, 1060, 1061,
               1062, 1063, 1066, 1523, 1054, 2059, 1760, 1364, 1253, 1537, 2358, 2171, 1864, 1889, 2060, 1776, 2568,
               2652, 1538, 2451, 2452, 2455, 2191, 1060, 1061, 1062, 1063, 1532, 1532, 1534, 1360, 1354, 2766, 2061,
               2062, 1865, 1865, 2557, 1583, 1068, 2065, 2349, 1031, 2558, 1364, 1378, 2653, 2655, 1253, 2542, 2542,
               2542, 2542, 1436, 1540, 2748, 1069, 1612, 1960, 1961, 1002, 2359, 1463, 1235, 1366, 1331, 1966, 1866,
               1460, 1201, 1202, 1203, 1070, 2762, 1950, 1951, 2360, 2361, 2362, 2367, 2559, 2140, 1965, 1541, 2657,
               2169, 2170, 2171, 2269, 2169, 2368, 2767, 2768, 1867, 2136, 2137, 2769, 2151, 2151, 1508, 1254, 1230,
               2458, 1542, 2770, 1534, 2370, 1966, 2364, 2131, 1367, 1969, 2118, 2119, 2120, 2120, 1331, 1368, 1071,
               1543, 2561, 2562, 1970, 1971, 1952, 1952, 1550, 1255, 2563, 1906, 1560, 1256, 1701, 2040, 2055, 2060,
               2066, 2066, 2066, 2564, 2771, 2067, 1340, 1257, 1370, 1370, 2070, 1770, 1223, 1464, 1464, 1545, 1546,
               1072, 2564, 2565, 2493, 2364, 1230, 1063, 2163, 2725, 2726, 2143, 2144, 2145, 1002, 1430, 1330, 2703,
               1074, 2127, 2366, 2659, 1824, 1096, 2748, 1373, 2660, 2375, 1258, 1560, 1075, 1075, 1982, 2661, 1561,
               1843, 1260, 1940, 2649, 1760, 2662, 2169, 1368, 1255, 2071, 2453, 2663, 2190, 1050, 2664, 1073, 1745,
               1772, 1550, 1259, 1077, 1562, 1101, 1102, 1103, 1104, 1105, 1106, 1107, 1108, 1109, 1111, 1115, 1118,
               1119, 1128, 1129, 1138, 1139, 1144, 1151, 1152, 1199, 2171, 2206, 1564, 1564, 1467, 1262, 1263, 2180,
               2357, 1344, 2493, 2072, 1775, 1518, 1566, 1776, 1375, 1590, 1907, 2777, 2348, 2780, 2783, 2536, 1468,
               1876, 1079, 1080, 2568, 2573, 2575, 1034, 1983, 1469, 1474, 2666, 2153, 1376, 1441, 1879, 1879, 1264,
               2125, 1568, 1569, 1230, 1654, 1718, 2568, 2573, 2468, 1880, 1081, 2081, 2451, 2452, 2453, 2454, 2455,
               2536, 1835, 1082, 2571, 1083, 1364, 1378, 1223, 2471, 2472, 2477, 2479, 1778, 2340, 1570, 1603, 2457,
               2481, 2482, 2481, 2667, 1379, 1380, 1984, 1720, 2668, 1238, 1885, 1583, 2379, 1585, 2669, 1084, 2573,
               1742, 1026, 1342, 2670, 2574, 1034, 1472, 2339, 2671, 1038, 1088, 1339, 2672, 1905, 2155, 2156, 1586,
               1985, 2465, 1245, 1960, 2169, 2132, 1602, 2144, 1089, 1090, 1266, 1266, 2575, 1474, 1568, 2576, 1092,
               1039, 2673, 1581, 1581, 1583, 1585, 1085, 1086, 1886, 1027, 1441, 1473, 2493, 1022, 2790, 2791, 2090,
               2188, 2189, 2190, 2191, 2188, 2190, 1093, 1094, 2381, 1588, 2382, 1095, 1590, 1590, 1096, 1267, 1013,
               1887, 1477, 1475, 1477, 1890, 1270, 2145, 2152, 1801, 1813, 1815, 1888, 2170, 2543, 2543, 1784, 1601,
               1602, 1603, 1604, 1605, 1606, 1607, 1608, 1609, 1610, 1612, 1613, 1614, 1615, 1653, 1654, 1655, 1097,
               1098, 2093, 2675, 2675, 1367]


def check_unique():
    """
    Returns a tuple with the original merged zipcode supplier companies and the number of unique suppliers
    :return:
    """

    path = r'results_MA'  # use your path
    all_files = glob.glob(path + "/*.csv")

    li = []
    print(f"The number of zipcodes checking for unique are :: ", len(all_files))
    for filename in all_files:
        df = pd.read_csv(filename, index_col=None, header=0, encoding='utf-8')
        li.append(df)

    df = pd.concat(li, axis=0, ignore_index=True)
    # Deleting Zipcode and Date_Downloaded columns from the Dataframe
    df.__delitem__('Zipcode')
    df.__delitem__('Date_Downloaded')
    # Changing NaN values in the df to None python
    df = df.where((pd.notnull(df)), None)
    print(df.drop_duplicates().to_string())
    # Number of rows merged
    all_df_shape = df.shape[0]
    # Number of rows unique
    unique_df_shape = df.drop_duplicates().shape[0]
    print(f"\nMerged {len(all_files)} zipcodes rows :: ", all_df_shape)
    print(f"Unqiue {len(all_files)} zipcodes rows :: ", unique_df_shape)
    return all_df_shape, unique_df_shape


def convert_cents_to_dollars(x):
    """
    :param x: the string value in cents
    :return: a float value in dollars
    """
    # Finding all the text before the first space
    str_val = str(x).split(' ')[0]
    if str_val == 'None':
        return 0
    if str_val:
        return float(str_val) / 100


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


def get_suppliers(zipcode):
    """
    This function loops through each of the companies returned from the get_distribution_companies and gets the
    supplier's list for each of them
    :param production: to make sure CSV are not appended while testing the code
    :param zipcode: zipcode from massachusets
    :return: A csv file is saved
    """
    print("Performing scrape for ZIPCODE", zipcode)
    for dist_company in get_distribution_companies(zipcode=zipcode):
        company_id = dist_company['distributionCompanyId']
        company_name = dist_company['distributionCompanyName']
        is_municipal = dist_company['isMunicipalElectricCompany']
        if not is_municipal:
            post_data = dict(customerClassId="1",
                             distributionCompanyId=str(company_id),
                             distributionCompanyName=str(company_name),
                             monthlyUsage=600,
                             zipCode=zipcode)
            r2 = requests.post("http://www.energyswitchma.gov/consumers/compare", data=post_data)
            suppliers_list = json.loads(r2.text)
            df = pd.DataFrame.from_dict(suppliers_list)
            df = df[['supplierName', 'pricingStructureDescription', 'pricePerMonth', 'pricePerUnit',
                     'introductoryPrice', 'introductoryPrice', 'enrollmentFee', 'contractTerm',
                     'earlyTerminationDetailExport',
                     'hasAutomaticRenewal', 'automaticRenewalDetail',
                     'renewableEnergyProductPercentage', 'renewableEnergyProductDetail', 'otherProductServicesDetail',
                     'isDistributionCompany', 'estimatedCost', 'otherProductServices']]
            df["Zipcode"] = zipcode
            df["Date_Downloaded"] = datetime.today().strftime('%m/%d/%y %H:%M')

            df.columns = ['Supplier_Name', 'Rate_Type', 'Fixed_Charge', 'Variable_Rate', 'Introductory_Rate',
                          'Introductory_Price_Value', 'Enrollment_Fee', 'Contract_Term',
                          'Early_Termination_Fee', 'Automatic_Renewal_Type', 'Automatic_Renewal_Detail',
                          'Percent_Renewable', 'Renewable_Description', 'Incentives_Special_Terms', 'Incumbent_Flag',
                          'Estimated_Cost', 'Other_Product_Services', 'Zipcode', 'Date_Downloaded']
            df['Variable_Rate'] = df['Variable_Rate'].apply(convert_cents_to_dollars)
            df['Introductory_Rate'] = df['Introductory_Price_Value'].apply(lambda x: True if x else False)

            if Path(f'results_MA/{zipcode}.csv').is_file():
                print("Appending to the existing CSV file ...")
                with open(f'results_MA/{zipcode}.csv', 'a') as f:
                    df.to_csv(f, index=False, header=False)
            else:
                print("Writing to a new CSV file ...")
                df.to_csv(f'results_MA/{zipcode}.csv', index=False)
            return True
    return False


def scrape():
    """
    This is the main function to scrape the results
    :return: None
    """
    # Prints the timestamp to see how long the program takes
    print(datetime.today(), '\n\n\n')
    success = 0

    # Clears the results_MA director on each run
    for file in os.listdir('results_MA'):
        os.remove(f'results_MA/{file}')
    # Formats the zipcodes in the right format
    zipcodes_ma_0 = list(map(lambda x: '0' + str(x), ma_zipcodes))
    print("The number of zipcodes we will run the script for is:", len(zipcodes_ma_0))
    # Calls the server for first 150 zipcode
    for zip in zipcodes_ma_0[:150]:
        print("Running for zipcode:", zip)
        if get_suppliers(zipcode=str(zip)):
            success += 1
    # The success variable to see how many zipcodes were actually extracted
    print(f'The number of zipcodes successfully scraped are: {success}')

    print(datetime.today())


if __name__ == '__main__':
    scrape()
    # check_unique()
