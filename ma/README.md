# Massachussets 
Term: Fall 2019 (Updated Spring 2020)
Links: [energyswitchma.gov](http://www.energyswitchma.gov/#/), [Youtube Demonstration](https://www.youtube.com/watch?v=hpB_RoIlrFI&list=PLpSsC5dbVHV-Uf1VJ2ekMPUIohRoZYe8n&index=1)

### Packages required for running MA
Install everything in `\ma\requirements.txt`

### Quickstart
1. In the **\\ma\\**, open `req_method.py` file.
2. In the `scrape()` function in the file, change the items marked [ACTION REQUIRED] and choose the number of zip codes to analyze.

### Running the script                                           
4. Call  `scrape()` function in the main code block (marked as [ACTION REQUIRED]).
5. After the zip code level CSV file has been downloaded in the `results_MA` folder, you can now replace the main code block to call the function `check_unique()` and can comment out `scrape()`.
