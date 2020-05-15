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

#### Run

**NOTE: the scripts need to be executed from the PowerToChoose folder or else it will fail**
