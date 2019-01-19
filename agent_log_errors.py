
import re
import os
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()
os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')

# Might want to change the strip function to return a tuple holding the timestamp for each unique log
# thus being able to rejoin them later for display, revealing the time of the first occurences.
# Better still, create arrays to not only reconstruct the log entry with timestamp, but also show counts
# for the number of times that error occurred in the file
# def strip_timestamp(error_log):
#         stripped = error_log[20:]
#         return stripped

# def is_last_stamp(current_stamp, match_list):

def log_breakdown(error_log):
    breakdown = {
        "first_stamp": error_log[:20],
        "message": error_log[20:],
        "last_stamp": error_log[:20],
        "count": 1
    }
    return breakdown

selected_path = filedialog.askdirectory()
# might use command prompt to allow user to chooose selecting a folder or selecting a file
# selected_path = filedialog.askopenfilename()

for dir in os.walk(selected_path):
    if "logs" in dir[1]:
        logs_path = f"{dir[0]}/logs"
    elif "log" in dir[1]:
        logs_path = f"{dir[0]}/log"

logs_directory = os.fsencode(logs_path)
for file in os.listdir(logs_directory):
    filename = os.fsdecode(file)
    if type(logs_directory) == bytes:
        logs_directory = logs_directory.decode("utf-8")
    file_path = f"{logs_directory}/{filename}"

    match_list = []
    with open(file_path) as file:
        for line in file:
            if "ERROR" in line: #function to abstract out this step perhaps
                message = log_breakdown(line)['message']
                if len(match_list) == 0:
                    match_list.append(log_breakdown(line))
                # elif any(d['message'] == message for d in match_list):
                #     if datetime.strptime(d['last_stamp'])
                elif not any(d['message'] == message for d in match_list): #log_breakdown(line)['message'] not in match_list:
                    match_list.append(log_breakdown(line))

    print("-------------------------------------------------------------------------------")
    print(f"{filename} - Total unique errors: {match_list.__len__()}")
    print("-------------------------------------------------------------------------------")

    for error in match_list:
        print("COUNT: {} // FIRST STAMP: {} // LAST STAMP: {}".format(error['count'], error['first_stamp'], error['last_stamp']))
        print("MESSAGE: {}".format(error['message']))

# arg parse module
# first and last timestamp of error type
# multi-string search to find combination of error with another term by adding an optional arg
# show me most common agent, most common integration, most common error from optional argument
# recommends sorting by count

# compare config check.log vs yaml for each integration config to determine possible config errors (beyond just yaml)
    # config check may not have a value that looks to be correctly configed and passed yaml check
    # would need to use python yaml parser to create dict and check it against dict from config yaml
# summary of differences between runtime config dump against datadog.yaml

# try to use python modules
# https: // docs.python.org/2/library/argparse.html
# https: // pyyaml.org/wiki/PyYAMLDocumentation
