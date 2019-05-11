
import re
import os #for accessing local file system
import argparse #for taking arguments when running the script
import subprocess #ability to run bash command for yaml linting 
import tkinter as tk
from tkinter import filedialog #supports prompt of local macOS file selector window
from datetime import datetime
from prettytable import PrettyTable

# handle optional arguments for sorting logs output, finding error logs with key terms, etc
parser = argparse.ArgumentParser()
parser.add_argument('-s', '--sort', choices=['count', 'last_stamp'], default='first_stamp', help='Sort logs in descending order by selected attribute')
parser.add_argument('-w', '--warn', action='store_true', help='Include warning logs in the output')
parser.add_argument(
    '-t', '--term', help='Find unique errors containing an additional term ie the name of a check, integration, symptom (note: term is case sensitive matching)')
parser.add_argument('-lf', '--log_file', action='store_true', help='Trigger prompt to select a particular log file from a list of filenames')
parser.add_argument('-y', '--yaml', action='store_false', help='Flag to disable yaml linting output')
parser.add_argument('-ne', '--no_edit', action='store_false', help='Flag to avoid opening flare in code editor')

args = parser.parse_args()

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
if len(selected_path) <= 1:
    print("\nIt appears a flare directory was not selected. Please try again  ( ͡° ͜ ͡°)\n")
    exit()
    

# open flare in selected code editor
if args.no_edit:
    return_focus()
    print("\n1. VSCode")
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
    print("\n-------------------------------------------------------------------------------")
    print(f"{filename} - Total unique errors: {match_list.__len__()} (sorted by {args.sort})")
    print("-------------------------------------------------------------------------------")
    for error in match_list:
        print("COUNT: {} -- FIRST STAMP: {} -- LAST STAMP: {}".format(error['count'], error['first_stamp'], error['last_stamp']))
        print("MESSAGE: {}".format(error['message']))


# YAML CONFIG VALIDATION MAIN EXECUTION OF BUSINESS LOGIC - loop through yaml files and run bash linter on each
if args.yaml != False:
    print("\n///////////////////////////////////////////////////////////////////////////////")
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

# -------------------------------
# misc configurations/info
# -------------------------------
print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
print("MISCELLANEOUS CONFIGS/INFO")
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

def find_file(names, path):
    for root, dirs,files in os.walk(path):
        for name in names:
            if name in files:
                return os.path.join(root, name)

# summarize status.log/info.log
status_info_path = find_file(["status.log", "info.log"], selected_path) #may need to reconsider this as it seems some agent 5 flares can have both status.log and info.log so it will find the status.log but not contain any of the agent 5 matches
print(f"Summary of {status_info_path}:")
with open(status_info_path) as file:
    for line in file:
        if re.match(r'(?<!\S)Agent \(v', line):
            print(f"    {line.rstrip()}")
        elif "Collector (v" in line:
            print(f"    Agent Version: {line[10:].rstrip()}")
        if "  os:" in line:
            print(line.rstrip())
        if "  platformVersion:" in line:
            print(line.rstrip())
        if "  hostname:" in line:
            print(line.rstrip())
        if "NTP offset:" in line:
            print(line.rstrip())
        if "Check Runners:" in line:
            print(f"  {line.rstrip()}")

# rows for comparison table of configs from datadog.yaml/runtime_config_dump.yaml/envvars.log
log_levels = ['log_level:', 'N/A', 'N/A', 'N/A']
apm_enabled = ['apm_enabled:', 'N/A', 'N/A', 'N/A']
logs_enabled = ['logs_enabled:', 'N/A', 'N/A', 'N/A']
check_runners = ['check_runners:', 'N/A', 'N/A', 'N/A']
use_dogstatsd = ['use_dogstatsd:', 'N/A', 'N/A', 'N/A']
dogstatsd_non_local_traffic = ['dogstatsd_non_local_traffic:', 'N/A', 'N/A', 'N/A']

def get_config_val(line):
    return re.search(r'(?<=: )[^\]]+', line.rstrip()).group(0)

# summarize datadog.yaml/.conf
try:
    datadog_conf_path = find_file(["datadog.yaml", "datadog.conf"], selected_path)
    with open(datadog_conf_path) as file:
    # consider refactoring the loop below into a function shared by runtime dump
        for line in file:
            if "log_level:" in line:
                log_levels[1] = get_config_val(line)
            if "apm_config:" in line:
                apm_enabled[1] = re.search(r'(?<=: )[^\]]+', next(file)[2:].rstrip()).group(0)
            if "logs_enabled:" in line:
                logs_enabled[1] = get_config_val(line)
            if "check_runners:" in line:
                check_runners[1] = get_config_val(line)
            if "use_dogstatsd:" in line:
                use_dogstatsd[1] = get_config_val(line)
            if "dogstatsd_non_local_traffic:" in line:
                dogstatsd_non_local_traffic[1] = get_config_val(line)
except:
    pass

# summarize runtime config dump
try:
    runtime_conf_path = find_file(["runtime_config_dump.yaml"], selected_path)
    with open(runtime_conf_path) as file:
    # consider refactoring the loop below into a function ddyaml
        for line in file:
            if "log_level:" in line:
                log_levels[2] = get_config_val(line)
            if "apm_config:" in line:
                apm_enabled[2] = re.search(r'(?<=: )[^\]]+', next(file)[2:].rstrip()).group(0)
            if "logs_enabled:" in line:
                logs_enabled[2] = get_config_val(line)
            if "check_runners:" in line:
                check_runners[2] = get_config_val(line)
            if "use_dogstatsd:" in line:
                use_dogstatsd[2] = get_config_val(line)
            if "dogstatsd_non_local_traffic:" in line:
                dogstatsd_non_local_traffic[2] = get_config_val(line)
except:
    pass

def get_envvar(line):
    return re.search(r'(?<==)[^\]]+', line.rstrip()).group(0)

#summarize envvars.log
try:
    envvars_path = find_file(["envvars.log"], selected_path)
    with open(envvars_path) as file:
        for line in file:
            if "-  DD_LOG_LEVEL=" in line:
                log_levels[3] = get_envvar(line)
            if "-  DD_APM_ENABLED" in line:
                apm_enabled[3] = get_envvar(line)
            if "-  DD_LOGS_ENABLED" in line:
                logs_enabled[3] = get_envvar(line)
            if "-  DD_CHECK_RUNNERS" in line:
                check_runners[3] = get_envvar(line)
            if "-  DD_DOGSTATSD_ENABLED" in line:
                use_dogstatsd[3] = get_envvar(line)
            if "-  DD_DOGSTATSD_NON_LOCAL_TRAFFIC" in line:
                dogstatsd_non_local_traffic[3] = get_envvar(line)
except:
    pass

# print a comparison table for configs from their various sources
print("\nNOTE: envvar.log values take precedence over runtime_config_dump.yaml and the config dump over datadog.yaml")
print("NOTE: Table does not support agent v5 so check datadog.conf for configs")
t = PrettyTable(['', 'datadog.yaml', 'runtime_config_dump.yaml', 'envvars.log'])
t.add_row(log_levels)
t.add_row(apm_enabled)
t.add_row(logs_enabled)
t.add_row(check_runners)
t.add_row(use_dogstatsd)
t.add_row(dogstatsd_non_local_traffic)
print(t)

# show most common agent, most common integration, most common error from optional argument
# compare config check.log vs yaml for each integration config to determine possible config errors (beyond just yaml)
    # config check may not have a value that looks to be correctly configed and passed yaml check
    # would need to use python yaml parser to create dict and check it against dict from config yaml
# summary of differences between runtime config dump against datadog.yaml

# https://pyyaml.org/wiki/PyYAMLDocumentation
# https://yamllint.readthedocs.io/en/stable/quickstart.html#running-yamllint
# https://pypi.org/project/PrettyTable/
