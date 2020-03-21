import pdfplumber as plum
import camelot

PDF_FILE = "../PDFs/1880.pdf"


def pdfplumber_extraction():
    pdf = plum.open(PDF_FILE)
    first_page = pdf.pages[0]
    for index, word in enumerate(first_page.extract_words()):
        print(word)


def camelot_extraction(pdf_filepath):
    tables = camelot.read_pdf(pdf_filepath)
    print("The number of tables found in the PDF:", len(tables))
    if len(tables) > 0:
        print(tables[0].df.to_string())


camelot_extraction(r"..\PDFs\59.pdf")

"""
Notes from the meeting w Jenya 
    - Machine Learning 
        - Categorical Data 
        - Paragraphs
        - Tabular
        - You can use popup box as a training set 
    - You can use bounding boxes
    
         
"""