import tdu_parse, tdu_scrape_headless, var_parse, var_scrape_headless, email_error
from pathlib import Path
from datetime import datetime as dt
import datetime as Dt
import traceback
import os
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)
sys.path.append(dir_path)
print(dir_path)

# Function to scrape and parse all past variabel rates
def pvd_total():
    var_scrape_headless.scrape('ES')
    var_parse.run('ES')
    var_scrape_headless.scrape('UI')
    var_parse.run('UI')

def run_all():
    # Get current datetime
    x=dt.today()
    
    # Scrape and parse offers
    tdu_scrape_headless.scrape('es')
    tdu_parse.run('es')
    
    tdu_scrape_headless.scrape('ui')
    tdu_parse.run('ui')
    
    # Check whether we have already scraped past variable rates today **note: shoudl add diff checker at some pt and will have to change this
    scraped = os.path.exists(
            "./data/"+ "PVD_ES_"+ str(Dt.date.today()) + ".csv") and os.path.exists(
                    "./data/"+ "PVD_UI_"+ str(Dt.date.today()) + ".csv")
    
    # Scrape and parse past variable rates (if the hour is 5am or if the previous attempt failed)
    if (x.hour >= 5) and not(scraped):
        pvd_total()

# Run all and send email with traceback if any unknown errors occur

try:
    run_all()
    if not Path('run_history.txt').is_file():
        with open('run_history.txt', 'w') as run_file:
            run_file.write(dt.today().strftime('%m/%d/%y %H:%M:%S'))
    else:
        with open('run_history.txt', 'a', newline='') as run_file:
            run_file.write("\n" + dt.today().strftime('%m/%d/%y %H:%M:%S'))
except Exception as e:
    error_traceback = traceback.extract_tb(e.__traceback__)
    email_error.send_email(error=f"Traceback at {dt.today().strftime('%m/%d/%y %H:%M:%S')} from Scheduler: {error_traceback}")

# OLD
#from threading import Timer
# Specify when to run the past variable rates scraper
#y=x.replace(day=x.day+1, hour=6, minute=0, second=0, microsecond=0)
#delta_t=y-x
#secs=delta_t.seconds+1
#t = Timer(secs, pvd_total())
#t.start()