# flare_spotter

Currently, this script can be an essential time saver when conducting an investgation about Datadog Agent related issues. Running the script opens a prompt for file selection on MacOS that is used to select the **unzipped** folder of the flare contents. It will quickly identify all unique errors/warnings found in Datadog Agent log files produced by a flare and has a number of CLI options for customizing log outputs.  It also includes a YAML linter supported by yamllint as discussed in installation instructions.

---
**Basic Usage**

Navigate to file directory (wherever you placed it) in terminal and run:

`python3 spotter.py`

![flare gun image](https://github.com/MikeTarkington/flare_spotter/blob/master/flare_gun.gif?raw=true)

---

**Setup**

- Download the `spotter.py` file from this respository

- Requires Installation of Python3. With xcode CLI tools and Homebrew installed already simply run the following (if you need either of the prerequisites see https://docs.python-guide.org/starting/install3/osx/):

    `brew install python `

- YAML linting requires installation of yamllint (https://yamllint.readthedocs.io/en/stable/index.html):

    `brew install yamllint `

**options help:**

```
-h --help
-s --sort choices=['count', 'last_stamp'], default='first_stamp help=Sort logs in descending order by selected attribute
-w --warn help=Flag to include warning logs in the output
-t --term help=Find unique errors containing an additional term ie the name of a check, integration, symptom (note: term is case sensitive matching)
-lf --log_file help=Trigger prompt to select a particular log file from a list of filenames
-y --yaml help=Disables output from yaml config file linter
```

**examples (can use many more combinations):**

Sort unique error and warning logs by count:

`python3 spotter.py -w -s count`

Unique error logs including the string "container" (case sensitive) from a particular file selected via CLI prompt:

`python3 spotter.py -lf -t container`

To disable the yaml linter:

`python3 spotter.py -y`

------------------------------------------------

Some Planned Features (as of 2/4/19)(strikethroughs completed)
- ~~add first and last time stamp to the outputs of each unique error log~~
- ~~support arguments passed with the run command that would enable search for unique logs with a particular term and also allow for combining the search for error logs containing a particular term (particularly useful for finding logs related to a specific check)~~
- optional argument to exclude logs containing specified string (reduce noisy outputs)
- consider less strict criteria for matching "unique" logs by having the matching process ignore differences that are found only in a certain stretch of characters (sometimes errors include object id's, hostnames, or other unqique items in the same type of error but this causes a lot of repeats to be recognized as unique).  there are troubleshooting tradeoffs to consider.
- ~~add count of occurrences for each error~~
    - show most common agent, integration, error from optional argument sorted by counts
- identify errors found in runtime config dump
- summary of differences between runtime config dump against datadog.yaml
- compare config check.log vs yaml for each integration config to determine possible config errors (beyond just yaml)
    - config check may not have a value that looks to be correctly configed and passed yaml check
    - would need to use python yaml parser to create dict and check it against dict from config yaml
- store unique errors in a database
    - support calls to the database for stastical analysis of flare error trends
    - provide mechanism for community sourced notes on significance of stored errors (a resource for solutions discovered in relation to a particular error)
- quick handles for searching errors in Zendesk, Trello, Wiki, and/or Google
- cli interactive log file selection with numbered list of log file names to choose from (flag argument triggers prompt)
