
import re
import os
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()
os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')

selected_path = filedialog.askdirectory()
# might use command prompt to allow user to chooose selecting a folder or selecting a file
# selected_path = filedialog.askopenfilename()

for dir in os.walk(selected_path):
    # print(dir[1])
    # print(type(dir[1][1]))
    if "logs" in dir[1]:
        logs_path = f"{dir[0]}/logs"

logs_directory = os.fsencode(logs_path)
for file in os.listdir(logs_directory):
    filename = os.fsdecode(file)
    if type(logs_directory) == bytes:
        logs_directory = logs_directory.decode("utf-8")
    file_path = f"{logs_directory}/{filename}"

    # Might want to change the strip function to return a tuple holding the timestamp for each unique log 
    # thus being able to rejoin them later for display, revealing the time of the first occurences.
    # Better still, create arrays to not only reconstruct the log entry with timestamp, but also show counts
    # for the number of times that error occurred in the file
    def strip_timestamp(error_log):
        stripped = error_log[20:]
        return stripped

    match_list = []
    with open(file_path) as file:
        for line in file:
            if "ERROR" in line:
                if len(match_list) == 0:
                    match_list.append(strip_timestamp(line))
                elif strip_timestamp(line) not in match_list:
                    match_list.append(strip_timestamp(line))

    print("-------------------------------------------------------------------------------")
    print(f"{filename} - Total unique errors: {match_list.__len__()}")
    print("-------------------------------------------------------------------------------")

    for error in match_list:
        print(error)

