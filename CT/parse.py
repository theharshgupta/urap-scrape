import bs4 as bs

with open('out.html') as ex:
    soup = bs.BeautifulSoup(ex, 'html.parser')

table = soup.find_all('table', class_ = "nice_table responsive highlight_table display nowrap")
table = table[0]
for row in table.find_all('tr'):
    for cell in row.find_all('td'):
        print(cell.attrs)
