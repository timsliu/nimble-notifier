# util.py
#
# utility functions common to multiple files

from pyzipcode import ZipCodeDatabase

zcdb = ZipCodeDatabase()

def zip_to_coors(zip_code):
    '''helper function converts zip code to lat lon coordinates'''

    try:
        zip_info = zcdb[zip_code]
        longitude = zip_info.longitude
        latitude = zip_info.latitude
    except KeyError as e:
        missing_zips = {94158: [37.771, -122.391]}
        longitude = missing_zips[zip_code][1]
        latitude  = missing_zips[zip_code][0]
        
    return [longitude, latitude]

def clean_email_address(email_address):
    '''changes an email address to all lower case and strips out spaces
    at the end'''
    email_address = email_address.lower()           # convert to lower case
    email_address = email_address.replace(' ', '')  # strip out spaces

    return email_address


def parse_by_suffix(input_string, suffix, start_char=" "):
    """searches through input_string until it finds the suffix. Walks backwards
    from the suffix and returns everything in the string between suffix and
    the end_char"""

    end = input_string.find(suffix)
    start = end

    while input_string[start] != start_char:
        start -= 1

    return input_string[start+1:end]

def parse_by_prefix(input_string, prefix, end_char=[" "]):
    """searches through input_string until it finds the prefix. Returns
    everything in the string between prefix and the next instance of
    end_char"""

    start = input_string.find(prefix) + len(prefix)
    end = start

    while input_string[end] not in end_char:
        end += 1
    return input_string[start:end]

def parse_by_line(input_string, prefix_string, offset):
    """breaks input string by lines and finds the index of the prefix_line.
    Returns the line that is offset past the prefix_line"""
 
    split_by_line = input_string.splitlines()
    prefix_line = split_by_line.index(prefix_string)

    return split_by_line[prefix_line + offset]


class APIUseExceededError(Exception):
    '''custom error class for when the API use is exceeded''' 
    pass
