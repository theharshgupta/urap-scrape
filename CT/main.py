import tdu_parse, tdu_scrape, var_parse, var_scrape
from datetime import datetime
from threading import Timer

def pvd_total():
    var_scrape.scrape('ES')
    var_parse.run('ES')
    var_scrape.scrape('UI')
    var_parse.run('UI')

x=datetime.today()
if x.hour > 6:
    y=x.replace(day=x.day+1, hour=6, minute=0, second=0, microsecond=0)
else:
    y=x.replace(day=x.day, hour=6, minute=0, second=0, microsecond=0)
delta_t=y-x

secs=delta_t.seconds+1

t = Timer(secs, pvd_total())

t.start()

tdu_scrape.scrape('es')
tdu_parse.run('es')

tdu_scrape.scrape('ui')
tdu_parse.run('ui')