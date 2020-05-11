# Texas - Fall 2019
This module is now deprecated. Go to https://github.com/theharshgupta/urap-scrape/tree/master/texas. 
#### Dependencies

| Name          | Installation Link                             | Purpose                                   |
| :---          |    :----:                                     |          :---:                            |
| Poppler       | https://poppler.freedesktop.org               | Used to perform OCR on PDfs               |
| wkhtmltopdf   | https://docs.bitnami.com/installer/apps/odoo/configuration/install-wkhtmltopdf/        | Used to convert HTML pages into PDFs      |

#### Possible Errors
### Running the script 
Authorized users can generate `credentials.json` from the Google Console and run `google.cloud` module in the script to run aforementioned functions. 

| Name          | Meaning                             | Fix                                   | Where |
| :---          |    :---:                           |          ---:                          | ---:  |
| TesseractNotFound | Invalid path to Tesseract | [link](https://stackoverflow.com/questions/50951955/pytesseract-tesseractnotfound-error-tesseract-is-not-installed-or-its-not-i) | ocr() function in pdfReader.py |
| No wkhtmltopdf executable found | Invalid path to wkhtmltopdf | [link](https://stackoverflow.com/questions/27673870/cant-create-pdf-using-python-pdfkit-error-no-wkhtmltopdf-executable-found) | downloadUsingPDFKit() function in scrapeHelpers.py |
## Scrape
`texas\main.py` manipulates data of a locally stored CSV of all the plans (downloaded from the main website).  First, Spanish data rows are filtered from the downloaded CSV. 
### PDF Downloading 
1. The `parse_csv` function takes the file path of the CSV 

#### Run

**NOTE: the scripts need to be executed from the PowerToChoose folder or else it will fail**
# New York

**IMPORTANT: make sure you have folders named "PDFs" and "Terms of Services" in the "PowerToChoose" folder (case-sensitive)**
1. Download/Clone the repository to a local folder. Follow the steps here [Github Cloning Repository](https://help.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository)

from the project folder, run:
```
cd PowerToChoose
python csv_generate.py <zip_code> <number_of_plans>
```
2. Enter the project folder in the terminal (make sure scrape.py is in your current directory)

example:
`python csv_generate.py 75001 10`
3. Run `python3 scrape.py`
