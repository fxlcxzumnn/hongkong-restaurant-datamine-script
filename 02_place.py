import json
import os
import sys
import _utils
import math
import datetime
import googlemaps
import time

VERSION = '1564966095'
TIMESTAMP = math.floor(datetime.datetime.now().timestamp())

conf_file = 'conf.json'
conf = _utils.read_json(conf_file)
data_path = conf['data_path']

fehd_path = os.path.join(data_path,'work','00_fehd','output.json')
fehd_data = _utils.read_json(fehd_path)
restaurant_list = fehd_data['restaurant_list']
#restaurant_list = restaurant_list[:10000]

def good_place_json(json_path):
    if not os.path.isfile(json_path): return False
    data = _utils.read_json(json_path)
    if 'version' not in data: return False
    if data['version'] != VERSION: return False
    if TIMESTAMP - data['timestamp'] >= 365*24*60*60: return False
    return True

gmaps = googlemaps.Client(key=conf['google_maps_api_key'])

for restaurant in restaurant_list:
    licno = restaurant['LICNO']
    geocode_path = _utils.get_geocode_restaurant_path(licno)
    #print(restaurant_path)

    geocode_json_path = os.path.join(geocode_path, 'geocode.json')
    geocode_json = _utils.read_json(geocode_json_path)
    geocode_list = geocode_json["geocode_en"] + geocode_json["geocode_tc"]
    #print(geocode_list)

    for geocode in geocode_list:
        #print(geocode)
        place_id = geocode['place_id']
        place_path = _utils.get_s02_place_path(place_id)
        _utils.mkdirs(place_path)
        
        json_path = os.path.join(place_path, 'place.json')
        if good_place_json(json_path):
            print('ignore good place, place_id={place_id}'.format(place_id=place_id))
            continue
        
        print('download place, place_id={place_id}'.format(place_id=place_id))
        
        place_result_en = gmaps.place(place_id=place_id, language='en')
        place_result_tc = gmaps.place(place_id=place_id, language='zh-HK')

        output_data = {
            'place_id': place_id,
            'place_en': place_result_en,
            'place_tc': place_result_tc,
            'timestamp': TIMESTAMP,
            'version': VERSION,
        }
        _utils.write_json(output_data, json_path)
