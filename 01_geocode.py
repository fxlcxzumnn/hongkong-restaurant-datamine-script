import json
import os
import sys
import _utils
import math
import datetime
import googlemaps

VERSION = '1564894996'
TIMESTAMP = math.floor(datetime.datetime.now().timestamp())

conf_file = 'conf.json'
conf = _utils.read_json(conf_file)

data_path = conf['data_path']

fehd_path = os.path.join(data_path,'work','00_fehd','output.json')
fehd_data = _utils.read_json(fehd_path)
restaurant_list = fehd_data['restaurant_list']
restaurant_list = restaurant_list[:5]

output_path_root = os.path.join(data_path,'work','01_geocode')

def good_geocode_json(json_path):
    if not os.path.isfile(json_path): return False
    geocode_data = _utils.read_json(json_path)
    if 'version' not in geocode_data: return False
    if geocode_data['version'] != VERSION: return False
    if TIMESTAMP - geocode_data['timestamp'] >= 365*24*60*60: return False
    return True

gmaps = googlemaps.Client(key=conf['google_maps_api_key'])

for restaurant in restaurant_list:
    licno = restaurant['LICNO']
    licno_md5 = _utils.md5(licno)
    restaurant_path = os.path.join(
        output_path_root,
        licno_md5[0],
        licno_md5[1],
        licno_md5[2],
        licno
    )
    _utils.mkdirs(restaurant_path)
    
    json_path = os.path.join(restaurant_path, 'geocode.json')
    if good_geocode_json(json_path):
        print('ignore good geocode, licno={licno}'.format(licno=licno))
        continue

    print('download geocode, licno={licno}'.format(licno=licno))

    geocode_result_en = gmaps.geocode(restaurant['ADR_EN'])
    geocode_result_tc = gmaps.geocode(restaurant['ADR_TC'])

    output_data = {
        'licno': licno,
        'adr_en': restaurant['ADR_EN'],
        'adr_tc': restaurant['ADR_TC'],
        'geocode_en': geocode_result_en,
        'geocode_tc': geocode_result_tc,
        'timestamp': TIMESTAMP,
        'version': VERSION,
    }
    _utils.write_json(output_data, json_path)
