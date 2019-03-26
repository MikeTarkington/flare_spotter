import os #for accessing local file system
import argparse #for taking arguments when running the script
import subprocess #ability to run bash command for yaml linting 
import tkinter as tk
import re # regex package
from tkinter import filedialog #supports prompt of local macOS file selector window
from datetime import datetime

# handle optional arguments for sorting logs output, finding error logs with key terms, etc
parser = argparse.ArgumentParser()
parser.add_argument('-s', '--sort', choices=['count', 'last_stamp'], default='first_stamp', help='Sort logs in descending order by selected attribute')
parser.add_argument('-w', '--warn', action='store_true', help='Include warning logs in the output')
parser.add_argument(
    '-t', '--term', help='Find unique errors containing an additional term ie the name of a check, integration, symptom (note: term is case sensitive matching)')
parser.add_argument('-lf', '--log_file', action='store_true', help='Trigger prompt to select a particular log file from a list of filenames')
parser.add_argument('-y', '--yaml', action='store_false', help='Flag to disable yaml linting output')
parser.add_argument('-ne', '--no_edit', action='store_false', help='Flag to avoid opening flare in code editor')
parser.add_argument('-re', '--exclude_string', action='store', help='Enter regex or string to exclude when parsing logs')
parser.add_argument('-ll', '--loosen_logs', action='store_true', help='Loosen matching requirements for log errors. I.e. different hosts but same error will be countered as 1 and not 2 errors.')


args = parser.parse_args()

# key: error, value: list of error messages
err_dict = dict()

def get_error_key(message):
    # get 1 or more characters so long as they're not bars. will mean that it breaks our log string up into different matching group | g1 | g2 | ...
    error_key_regex = re.compile('([^\|]+)')
    # find all to emulate global flag
    return error_key_regex.findall(message)[2] # matched group is 2nd since 0th is timezone, 1st is error type
    

def get_error_message(message):
    # each match will be the the strings between the | and we'll get the last matching one (the actual error message)
    error_message_regex = re.compile('([^\|]+$)')
    return error_message_regex.search(message).group() # we really should only ever receive one result here


# builds a dict of lists where k is error and elements of list are the messages
# example of err message format: <timezone> | <error type> | (<file>:<line> in <fucntion>) | <some error message>
def build_errors(message):
    try:
        er_key = get_error_key(message)
        er_message = get_error_message(message)
        if er_key in err_dict:
            err_dict[er_key].append(er_message)
        else:
            err_dict[er_key] = [er_message]
    except:
        print("We've occured some error building our non-unique logging dictionary.")

def print_dict():
    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^UNIQUE LOGGING ERRORS^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    for k, v in err_dict.items():
        print("ERROR AT LOCATION: {}\n\t # OF ERRORS FOUND: {}\n\t ERROR LOOKS LIKE: {}".format(k, len(v), v[0]))
    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")


def return_focus():
    root = tk.Tk()
    root.withdraw()
    os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')

return_focus()

def log_breakdown(error_log):
    breakdown = {
        "first_stamp": datetime.strptime(error_log[:19], "%Y-%m-%d %H:%M:%S"),
        "message": error_log[20:],
        "last_stamp": datetime.strptime(error_log[:19], "%Y-%m-%d %H:%M:%S"),
        "count": 1
    }
    return breakdown

# prompt user to enter path to folder of the flare
selected_path = filedialog.askdirectory()
# open flare in selected code editor
if args.no_edit:
    return_focus()
    print("1. VSCode")
    print("2. Atom")
    print("3. Sublime 3")
    print("...or press Return to skip (Note: Using -ne flag prevents this dialog.)")
    editor_num = input("Select the code editor above to open this flare directory (must be installed in Applications folder): ")
    
    if editor_num == "1":
        try:
            subprocess.Popen(['/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code', selected_path])
        except:
            print("\n**It seems VSCode is not installed in the Applications directory.\n**")
    elif editor_num == "2":
        try:
            subprocess.Popen(['/Applications/Atom.app/Contents/Resources/app/atom.sh', selected_path])
        except:
            print("\n**It seems Atom is not installed in the Applications directory.\n**")
    elif editor_num == "3":
        try:
            subprocess.Popen(['/Applications/Sublime Text.app/Contents/SharedSupport/bin/subl', selected_path])
        except:
            print("\n**It seems Sublime is not installed in the Applications directory.\n**")
    else:
        print("\n**Skipped opening the flare in a code editor**\n")

# find log files directory for either agent v5 or 6
for dir in os.walk(selected_path):
    if "logs" in dir[1]:
        logs_path = f"{dir[0]}/logs"
    elif "log" in dir[1]:
        logs_path = f"{dir[0]}/log"

# fuction to build a matched list of logs meeting the criteria for inclusion
def build_log_matches(line, log_regex=None):
    # if we have a regex obj, and we've found our rejex on the line
    if (log_regex != False and log_regex.search(line)): # won't return truthy if search fails
        return None # early return
    message = log_breakdown(line)['message']
    # if we have non-unique logs enabled
    if args.loosen_logs:
        build_errors(message)
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
# will either be a regex pattern obj or False depeneding of if we've gotten an arg supplied
log_regex = False if args.exclude_string == None else re.compile(args.exclude_string)

# if user has applied -lf to specify a particular log file
log_file_nums = {}
select_log_file = ""
if args.log_file:
    for i, file in enumerate(os.listdir(logs_directory)):
        print(f"{i} - {os.fsdecode(file)}")
        log_file_nums[i] = os.fsdecode(file)
    try:
        return_focus()
        selection = input("SELECT THE INTEGER CORRESPONDING TO THE DESIRED LOG FILE ABOVE: ")
        select_log_file = log_file_nums[int(selection)]
    except:
        print("ERROR: Ensure you select an integer from the list and not a string. Please rerun your command. Silly goose.")

for file in os.listdir(logs_directory):
    filename = os.fsdecode(file)
    if args.log_file == True and select_log_file != filename:
        continue
    if type(logs_directory) == bytes:
        logs_directory = logs_directory.decode("utf-8")
    file_path = f"{logs_directory}/{filename}"

    # open file and find unique errors storing first and last time stamp with repeat count
    match_list = []
    with open(file_path) as file:  # consider potential refactoring to abstract out steps from below
        if args.term:
            if args.warn:
                for line in file:
                    if ("WARN" in line or "ERROR" in line) and args.term in line:
                        build_log_matches(line, log_regex)
            else:
                for line in file:
                    if "ERROR" in line and args.term in line: 
                        build_log_matches(line, log_regex)
        else:
            if args.warn:
                for line in file:
                    if "WARN" in line or "ERROR" in line:
                        build_log_matches(line, log_regex)
            else:
                for line in file:
                    if "ERROR" in line:
                        build_log_matches(line, log_regex)

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

if (args.loosen_logs):
    print_dict();

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

