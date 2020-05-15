import tdu_parse, tdu_scrape, var_parse, var_scrape
from datetime import datetime
from threading import Timer

x=datetime.today()
y=x.replace(day=x.day+1, hour=14, minute=0, second=0, microsecond=0)
delta_t=y-x

secs=delta_t.seconds+1

t = Timer(secs, pvd_total())

t.start()
tdu_scrape.scrape('es')
tdu_parse.run('es')

tdu_scrape.scrape('ui')
tdu_parse.run('ui')

def pvd_total():
    var_scrape.scrape('ES')
    var_parse.run('ES')
    var_scrape.scrape('UI')
    var_parse.run('UI')