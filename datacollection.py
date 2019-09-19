from __future__ import absolute_import
​
from six.moves import range
​
from automation import CommandSequence, TaskManager
import sys
import time
# The list of sites that we wish to crawl
NUM_BROWSERS = int(sys.argv[2])
browser_mode = sys.argv[1]
​
sites = []
with open('top-250.csv','rb') as f:
    for line in f:
        line = line.replace('\n','')
	site = line.split(',')[1]
        sites.append("http://"+site)
# Loads the manager preference and 3 copies of the default browser dictionaries
manager_params, browser_params = TaskManager.load_default_params(NUM_BROWSERS)
​
# Update browser configuration (use this for per-browser settings)
for i in range(NUM_BROWSERS):
    # Record HTTP Requests and Responses
    browser_params[i]['http_instrument'] = True
    # Enable flash for all three browsers
    browser_params[i]['disable_flash'] = False
    if browser_mode == 'adblock':
        browser_params[i]['ublock-origin'] = True
    #browser_params[i]['headless'] = True
    browser_params[i]['js_instrument'] = True
    browser_params[i]['cookie_instrument'] = True
​
# Update TaskManager configuration (use this for crawl-wide settings)
manager_params['data_directory'] = '~/Desktop/'
manager_params['log_directory'] = '~/Desktop/'
if browser_mode == 'vanilla':
    print("Running VANILLA MODE..")
    time.sleep(10)
    manager_params['database_name'] = 'vanilla_mode.sqlite'
elif browser_mode =='adblock':
    manager_params['database_name'] = 'adblock_mode.sqlite'
    print("Running AD BLOCKING MODE..")
    time.sleep(10)
else:
    print "Wrong parameter for browser mode"
    exit(1)
# Instantiates the measurement platform
# Commands time out by default after 60 seconds
manager = TaskManager.TaskManager(manager_params, browser_params)
​
# Visits the sites with all browsers simultaneously
for site in sites:
    command_sequence = CommandSequence.CommandSequence(site)
​
    # Start by visiting the page
    command_sequence.get(sleep=10, timeout=60)
​
    # dump_profile_cookies/dump_flash_cookies closes the current tab.
    command_sequence.dump_profile_cookies(120)
​
    # index='**' synchronizes visits between the three browsers
    manager.execute_command_sequence(command_sequence, index=None)
​
# Shuts down the browsers and waits for the data to finish logging
manager.close()