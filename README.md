# urap-scrape
A repository for web scraping for URAP research project - Investigationg residential electricity prices in the US

# How to Run 

## Downloading the dependencies 

1. Download Chromedriver 76 or before (for Mac/Windows/Linux) [here](https://chromedriver.storage.googleapis.com/index.html?path=76.0.3809.126/)
    1. Unzip this, and make sure to add this to your project directory's root

### New York 

1. Download/Clone the repository to a local folder. Follow the steps here [Github Cloning Repository](https://help.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository)

2. Enter the project folder in the termal 

# Video Demos
### Video - Demo - New York

![](demo_videos/urap_scrape_demo.gif)

### Video - Demo - MA

![](demo_videos/ma.gif)

## Power to Choose  

### Run

from the project folder, run:
```
cd PowerToChoose
python csv_generate.py <zip_code> <number_of_plans>
```

example:
`python csv_generate.py 75001 10`
