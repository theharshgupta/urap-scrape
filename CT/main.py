import tdu_parse
import tdu_scrape
# import var_parse

tdu_scrape.scrape('es')
tdu_parse.run('es')

tdu_scrape.scrape('ui')
tdu_parse.run('ui')
# Past_Variable_Data_Parse()