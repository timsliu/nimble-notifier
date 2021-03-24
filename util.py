# util.py
#
# utility functions common to multiple files

from pyzipcode import ZipCodeDatabase

zcdb = ZipCodeDatabase()

def zip_to_coors(zip_code):
    '''helper function converts zip code to lat lon coordinates'''
        
    zip_info = zcdb[zip_code]
    return [zip_info.longitude, zip_info.latitude]

