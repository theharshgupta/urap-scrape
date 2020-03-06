import requests


def download_pdf(pdf_url, plan):
    """
    Function to download pdf's from the URL supplied
    :return: Saves the pdf in the PDF folder in the texas folder
    """
    pdf_url = str(pdf_url)
    url_extension = str(pdf_url).split('.')[-1]

    if url_extension == 'pdf':

        print(f"Trying to fetch {pdf_url}")
        response = requests.get(url=pdf_url, stream=True)

        with open(f"PDFs/{plan.idKey}.pdf", 'wb') as f:
            f.write(response.content)
