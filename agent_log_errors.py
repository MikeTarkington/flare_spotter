
import re
import os
import tkinter as tk
from tkinter import filedialog
from datetime import datetime

root = tk.Tk()
root.withdraw()
os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')

def log_breakdown(error_log):
    breakdown = {
        "first_stamp": datetime.strptime(error_log[:19], "%Y-%m-%d %H:%M:%S"),
        "message": error_log[20:],
        "last_stamp": datetime.strptime(error_log[:19], "%Y-%m-%d %H:%M:%S"),
        "count": 1
    }
    return breakdown

selected_path = filedialog.askdirectory()
# might use command prompt to allow user to chooose selecting a folder or selecting a file
# selected_path = filedialog.askopenfilename()

# find log files directory for either agent v5 or 6
for dir in os.walk(selected_path):
    if "logs" in dir[1]:
        logs_path = f"{dir[0]}/logs"
    elif "log" in dir[1]:
        logs_path = f"{dir[0]}/log"

# loop through and encode/decode current file in the log directory
logs_directory = os.fsencode(logs_path)
for file in os.listdir(logs_directory):
    filename = os.fsdecode(file)
    if type(logs_directory) == bytes:
        logs_directory = logs_directory.decode("utf-8")
    file_path = f"{logs_directory}/{filename}"

    # open file and find uqique errors storing first and last time stamp with repeat count
    match_list = []
    with open(file_path) as file:
        for line in file:
            if "ERROR" in line: #function to abstract out this step perhaps
                message = log_breakdown(line)['message']
                last_stamp = log_breakdown(line)['last_stamp']
                if len(match_list) == 0:
                    match_list.append(log_breakdown(line))
                elif not any(d['message'] == message for d in match_list):
                    match_list.append(log_breakdown(line))
                else:
                    for log_dict in match_list:
                        if log_dict['message'] == message and log_dict['last_stamp'] < last_stamp:
                            log_dict['last_stamp'] = last_stamp
                            log_dict['count'] += 1
    
    # print findings from found unique errors in current log file
    print("-------------------------------------------------------------------------------")
    print(f"{filename} - Total unique errors: {match_list.__len__()}")
    print("-------------------------------------------------------------------------------")
    for error in match_list:
        print("COUNT: {} // FIRST STAMP: {} // LAST STAMP: {}".format(error['count'], error['first_stamp'], error['last_stamp']))
        print("MESSAGE: {}".format(error['message']))

# arg parse module
# multi-string search to find combination of error with another term by adding an optional arg
# show most common agent, most common integration, most common error from optional argument
# option to sort by count

# compare config check.log vs yaml for each integration config to determine possible config errors (beyond just yaml)
    # config check may not have a value that looks to be correctly configed and passed yaml check
    # would need to use python yaml parser to create dict and check it against dict from config yaml
# summary of differences between runtime config dump against datadog.yaml

# try to use python modules
# https: // docs.python.org/2/library/argparse.html
# https: // pyyaml.org/wiki/PyYAMLDocumentation
