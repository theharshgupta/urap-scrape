import pdfplumber as plum
import camelot

PDF_FILE = "../PDFs/1880.pdf"


def pdfplumber_extraction():
    pdf = plum.open(PDF_FILE)

    first_page = pdf.pages[0]
    for index, word in enumerate(first_page.extract_words()):
        print(word)


def camelot_extraction():
    tables = camelot.read_pdf(PDF_FILE)
    if len(tables) > 0:
        tables[0].to_csv('foo.csv')


camelot_extraction()
