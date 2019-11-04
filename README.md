# Residential Electricity Price Scraping - UC Berkeley
A repository for web scraping for URAP research project - Investigationg residential electricity prices in the US

# How to Run 

Make sure you have Python 3 set up on your machine [Download Python](https://www.python.org/downloads/)

## Downloading the dependencies 

1. Download Chromedriver 76 or before (for Mac/Windows/Linux) [here](https://chromedriver.storage.googleapis.com/index.html?path=76.0.3809.126/)

    1. Unzip this, and make sure to add this to your project directory's root
    
2. Install all the project dependencies from `requirements.txt` using `pip install -r requirements.txt` (make sure when you run this command from your terminal, you are in your project directory)

    1. If your termninal does not recognize `pip`, try using `pip3` with the same command

### New York 

1. Download/Clone the repository to a local folder. Follow the steps here [Github Cloning Repository](https://help.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository)

2. Enter the project folder in the terminal (make sure scrape.py is in your current directory)

3. Run `python3 scrape.py`

### Massachussets 

# Video Demos
### Video - Demo - New York

![](demo_videos/urap_scrape_demo.gif)

### Video - Demo - MA

![](demo_videos/ma.gif)

## Power to Choose  

### Dependencies

poppler https://poppler.freedesktop.org

wkhtmltopdf https://wkhtmltopdf.org/downloads.html

### Run

from the project folder, run:
```
cd PowerToChoose
python csv_generate.py <zip_code> <number_of_plans>
```

example:
`python csv_generate.py 75001 10`
