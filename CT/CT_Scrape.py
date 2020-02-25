import bs4 as bs
import urllib.request


def open(website = 'https://www.energizect.com/compare-energy-suppliers'):
    source = urllib.request.urlopen(website).open()
    soup = bs.BeautifulSoup(source, 'lxml')
    return soup
