import bs4 as bs
<<<<<<< HEAD
from selenium import webdriver
import urllib.request
import time


def parse(website = 'https://www.energizect.com/compare-energy-suppliers'):
    # source = urllib.request.urlopen(website).open()
    source = requests.get(website)
    soup = bs.BeautifulSoup(source.content, 'html.parser')
    # soup = bs.BeautifulSoup(source, 'lxml')
    return soup

bs = parse()
html = bs.prettify() 
with open("out.txt","w") as out:
    for i in range(0, len(html)):
        try:
            out.write(html[i])
        except Exception:
            1+1