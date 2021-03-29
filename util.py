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

