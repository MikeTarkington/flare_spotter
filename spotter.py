
import re
import os #for accessing local file system
import argparse #for taking arguments when running the script
import subprocess #ability to run bash command for yaml linting 
import tkinter as tk
from tkinter import filedialog #supports prompt of local macOS file selector window
from datetime import datetime

# handle optional arguments for sorting logs output, finding error logs with key terms, etc
parser = argparse.ArgumentParser()
parser.add_argument('-s', '--sort', choices=['count', 'last_stamp'], default='first_stamp', help='Sort logs in descending order by selected attribute')
parser.add_argument('-w', '--warn', action='store_true', help='Include warning logs in the output')
parser.add_argument(
    '-t', '--term', help='Find unique errors containing an additional term ie the name of a check, integration, symptom (note: term is case sensitive matching)')
parser.add_argument('-lf', '--log_file', help='Specify name of log file to search rather than searching all') # use a try logic
parser.add_argument('-y', '--yaml', action='store_false', help='Flag to disable yaml linting output')
args = parser.parse_args()

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

# fuction to build a matched list of logs meeting the criteria for inclusion
def build_log_matches(line):
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

# MAIN EXECUTION OF BUSINESS LOGIC FOR LOGS - loop through and encode/decode current file in the log directory
logs_directory = os.fsencode(logs_path)
for file in os.listdir(logs_directory):
    filename = os.fsdecode(file)
    if args.log_file != None and args.log_file != filename:
        continue
    if type(logs_directory) == bytes:
        logs_directory = logs_directory.decode("utf-8")
    file_path = f"{logs_directory}/{filename}"

    # open file and find uqique errors storing first and last time stamp with repeat count
    match_list = []
    with open(file_path) as file:  # consider potential refactoring to abstract out steps from below
        if args.term:
            if args.warn:
                for line in file:
                    if ("WARN" in line or "ERROR" in line) and args.term in line:
                        build_log_matches(line)
            else:
                for line in file:
                    if "ERROR" in line and args.term in line: 
                        build_log_matches(line)
        else:
            if args.warn:
                for line in file:
                    if "WARN" in line or "ERROR" in line:
                        build_log_matches(line)
            else:
                for line in file:
                    if "ERROR" in line:
                        build_log_matches(line)

    # rearrange log match_list findings based on optional args prior to printing
    if args.sort == 'count':
        match_list = sorted(match_list, key=lambda k: k['count'], reverse=True)
    elif args.sort == 'last_stamp':
        match_list = sorted(match_list, key=lambda k: k['last_stamp'], reverse=True)


    # print findings from found unique errors in current log file
    print("-------------------------------------------------------------------------------")
    print(f"{filename} - Total unique errors: {match_list.__len__()} (sorted by {args.sort})")
    print("-------------------------------------------------------------------------------")
    for error in match_list:
        print("COUNT: {} -- FIRST STAMP: {} -- LAST STAMP: {}".format(error['count'], error['first_stamp'], error['last_stamp']))
        print("MESSAGE: {}".format(error['message']))


# YAML CONFIG VALIDATION MAIN EXECUTION OF BUSINESS LOGIC - loop through yaml files and run bash linter on each
if args.yaml != False:
    print("///////////////////////////////////////////////////////////////////////////////")
    print("YAML LINTING (requires install of https://yamllint.readthedocs.io/en/stable/index.html)")
    print("///////////////////////////////////////////////////////////////////////////////")
    try:
        # find yaml config files parent directory
        for dir in os.walk(selected_path):
            if "etc" in dir[1]:
                etc_path = f"{dir[0]}/etc"

        etc_directory = os.fsencode(etc_path)
        for file in os.listdir(etc_path):
            yaml_filename = os.fsdecode(file)
            subprocess.run(["yamllint", "-d", "relaxed", f"{etc_path}/{yaml_filename}"])
    except:
        print("**ERROR: yamllint must be installed to perform yaml linting steps - see https://yamllint.readthedocs.io/en/stable/index.html**")



# arg parse module
# multi-string search to find combination of error with another term by adding an optional arg
# show most common agent, most common integration, most common error from optional argument
# option to sort by count

# compare config check.log vs yaml for each integration config to determine possible config errors (beyond just yaml)
    # config check may not have a value that looks to be correctly configed and passed yaml check
    # would need to use python yaml parser to create dict and check it against dict from config yaml
# summary of differences between runtime config dump against datadog.yaml

# https://pyyaml.org/wiki/PyYAMLDocumentation
# https://yamllint.readthedocs.io/en/stable/quickstart.html#running-yamllint
