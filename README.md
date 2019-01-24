# flare_spotter

- Requires Installation of Python3

This script will quickly identify all unique errors found in Datadog Agent log files produced by a flare. Running the script opens a prompt for file selection on macOS that is used to select the unzipped folder of the flare contents.

Navigate to file directory in terminal and run:
`python3 agent_log_errors.py`

Some Planned Features (as of 1/18/19)(strikethroughs completed)
- ~~add first and last time stamp to the outputs of each unique error log~~
- support arguments passed with the run command that would enable search for unquie logs with a particular term and also allow for combining the search for error logs containing a particular term (particularly useful for finding logs related to a particular check)
- ~~add count of occurrences for each error~~
    - show most common agent, integration, error from optional argument sorted by counts
- Identify errors found in runtime config dump
- Summary of differences between runtime config dump against datadog.yaml
- compare config check.log vs yaml for each integration config to determine possible config errors (beyond just yaml)
    - config check may not have a value that looks to be correctly configed and passed yaml check
    - would need to use python yaml parser to create dict and check it against dict from config yaml
- store unique errors in a database
    - support calls to the database for stastical analysis of flare error trends
    - provide mechanism for community sourced notes on significance of stored errors (a resource for solutions discovered in relation to a particular error)
- quick handles for searching errors in Zendesk, Trello, Wiki, and/or Google
    
