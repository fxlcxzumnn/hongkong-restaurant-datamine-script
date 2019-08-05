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
#restaurant_list = restaurant_list[:10]

output_path_root = os.path.join(data_path,'work','01_geocode')

def good_geocode_json(json_path):
    if not os.path.isfile(json_path): return False
    geocode_data = _utils.read_json(json_path)
    if 'version' not in geocode_data: return False
    if geocode_data['version'] != VERSION: return False
    if TIMESTAMP - geocode_data['timestamp'] >= 365*24*60*60: return False
    return True

gmaps = googlemaps.Client(key=conf['google_maps_api_key'])

def now_ts():
    return datetime.datetime.now().timestamp()
last_call_api_ts = now_ts()

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
    
    name_en = restaurant['SS_EN']
    name_tc = restaurant['SS_TC']

    address_en = '{name_en}, {adr_en}'.format(name_en=name_en, adr_en=restaurant['ADR_EN'])
    address_tc = '{adr_tc} {name_tc}'.format(name_tc=name_tc, adr_tc=restaurant['ADR_TC'])

    #now_time = now_ts()
    #sleep_time = max(0,last_call_api_ts+1-now_time)
    #last_call_api_ts=now_time
    #time.sleep(sleep_time)
    geocode_result_en = gmaps.geocode(address=address_en, region='hk', language='en')

    #now_time = now_ts()
    #sleep_time = max(0,last_call_api_ts+1-now_time)
    #last_call_api_ts=now_time
    #time.sleep(sleep_time)
    geocode_result_tc = gmaps.geocode(address=address_tc, region='hk', language='zh-HK')

    output_data = {
        'licno': licno,
        'adr_en': address_en,
        'adr_tc': address_tc,
        'geocode_en': geocode_result_en,
        'geocode_tc': geocode_result_tc,
        'timestamp': TIMESTAMP,
        'version': VERSION,
    }
    _utils.write_json(output_data, json_path)
