import tdu_parse, tdu_scrape, var_parse, var_scrape

tdu_scrape.scrape('es')
tdu_parse.run('es')

tdu_scrape.scrape('ui')
tdu_parse.run('ui')

var_scrape.scrape('ES')
var_parse.run('ES')

var_scrape.scrape('UI')
var_parse.run('UI')