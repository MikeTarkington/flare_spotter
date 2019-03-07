import re

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