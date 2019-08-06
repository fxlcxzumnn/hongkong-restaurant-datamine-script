import json
import os
import sys
import _utils
import math
import datetime
import googlemaps
import time
import geopy.distance

VERSION = '1565104415'
TIMESTAMP = math.floor(datetime.datetime.now().timestamp())

conf = _utils.conf

fehd_data = _utils.read_json(_utils.s00_fehd_path)
fehd_list = fehd_data['restaurant_list']
#fehd_list = fehd_list[:10]

def get_place_data(place_id):
    s02_place_path = _utils.get_s02_place_path(place_id)
    s02_place_path = os.path.join(s02_place_path, 'place.json')
    return _utils.read_json(s02_place_path)

def good_output(path):
    if not os.path.isfile(path): return False
    data = _utils.read_json(path)
    if 'version' not in data: return False
    if data['version'] != VERSION: return False
    if TIMESTAMP - data['timestamp'] >= 365*24*60*60: return False
    return True

def find_geocode_place(merge_data, licno):
    geocode_path = _utils.get_geocode_restaurant_path(licno)
    geocode_json_path = os.path.join(geocode_path, 'geocode.json')
    geocode_json = _utils.read_json(geocode_json_path)
    
    geocode_en_list = geocode_json["geocode_en"]
    geocode_tc_list = geocode_json["geocode_tc"]

    if      ( len(geocode_en_list) == 1 ) \
        and ( len(geocode_tc_list) == 1 ) \
        and (geocode_en_list[0]['place_id'] == geocode_tc_list[0]['place_id']):

        place_data = get_place_data(geocode_en_list[0]['place_id'])
        merge_data['geocode_en'] = geocode_en_list[0]
        merge_data['geocode_tc'] = geocode_tc_list[0]
        merge_data['place_en'] = place_data['place_en']
        merge_data['place_tc'] = place_data['place_tc']
        return True, geocode_json, None

    place_id_to_place_data_dict = {}
    for geocode in geocode_en_list+geocode_tc_list:
        place_id = geocode['place_id']
        if place_id in place_id_to_place_data_dict: continue
        place_data = get_place_data(geocode['place_id'])
        if      ('permanently_closed' in place_data['place_en']['result']) \
            and place_data['place_en']['result']['permanently_closed']:
            continue
        place_id_to_place_data_dict[place_id] = place_data

    fehd_name_set = {fehd['SS_TC'].lower(), fehd['SS_EN'].lower()}
    match_name_place_id_list = []
    for place_id, place_data in place_id_to_place_data_dict.items():
        place_name_set = {
            place_data['place_tc']['result']['name'].lower(),
            place_data['place_en']['result']['name'].lower(),
        }
        inter_name_set = fehd_name_set & place_name_set
        if len(inter_name_set) > 0:
            match_name_place_id_list.append(place_id)

    if len(match_name_place_id_list) >= 1:
        latlong_list = match_name_place_id_list
        latlong_list = map(lambda i:place_id_to_place_data_dict[i],latlong_list)
        latlong_list = map(lambda i:i['place_en']['result']['geometry']['location'],latlong_list)
        latlong_list = map(lambda i:(i['lat'],i['lng']),latlong_list)
        if is_close(latlong_list):
            place_id = match_name_place_id_list[0]
            place_data = place_id_to_place_data_dict[place_id]
            for geocode in geocode_en_list:
                if geocode['place_id'] != place_id: continue
                merge_data['geocode_en'] = geocode
                break
            for geocode in geocode_tc_list:
                if geocode['place_id'] != place_id: continue
                merge_data['geocode_tc'] = geocode
                break
            merge_data['place_en'] = place_data['place_en']
            merge_data['place_tc'] = place_data['place_tc']
            return True, geocode_json, None

    match_name_place_id_list = []
    for place_id, place_data in place_id_to_place_data_dict.items():
        place_name_set = {
            place_data['place_tc']['result']['name'].lower(),
            place_data['place_en']['result']['name'].lower(),
        }
        name_good = False
        for fehd_name in fehd_name_set:
            for place_name in place_name_set:
                name_good = name_good or (fehd_name in place_name)
                name_good = name_good or (place_name in fehd_name)
        if name_good:
            match_name_place_id_list.append(place_id)

    if len(match_name_place_id_list) >= 1:
        latlong_list = match_name_place_id_list
        latlong_list = map(lambda i:place_id_to_place_data_dict[i],latlong_list)
        latlong_list = map(lambda i:i['place_en']['result']['geometry']['location'],latlong_list)
        latlong_list = map(lambda i:(i['lat'],i['lng']),latlong_list)
        if is_close(latlong_list):
            place_id = match_name_place_id_list[0]
            place_data = place_id_to_place_data_dict[place_id]
            for geocode in geocode_en_list:
                if geocode['place_id'] != place_id: continue
                merge_data['geocode_en'] = geocode
                break
            for geocode in geocode_tc_list:
                if geocode['place_id'] != place_id: continue
                merge_data['geocode_tc'] = geocode
                break
            merge_data['place_en'] = place_data['place_en']
            merge_data['place_tc'] = place_data['place_tc']
            return True, geocode_json, None
    
    return False, geocode_json, place_id_to_place_data_dict

def is_close(latlong_list):
    for latlong_0 in latlong_list:
        for latlong_1 in latlong_list:
            distance = geopy.distance.distance(latlong_0,latlong_1).meters
            if distance > 20: return False
    return True

miss_data_list = []

for fehd in fehd_list:
    licno = fehd['LICNO']

    merge_path = _utils.get_s03_merge_path(licno)
    _utils.mkdirs(merge_path)
    merge_path = os.path.join(merge_path,'merge.json')
    if good_output(merge_path):
        print('done ignore: licno={licno}'.format(licno=licno))
        continue

    merge_data = {
        'licno':licno,
        'fehd':fehd,
        'version':VERSION,
        'timestamp':TIMESTAMP,
    }
    
    good, geocode_json, place_id_to_place_data_dict = find_geocode_place(merge_data, licno)

    if good:
        print('good done: licno={licno}'.format(licno=licno))
        _utils.write_json(merge_data, merge_path)
    else:
        print('miss: licno={licno}'.format(licno=licno))
        for place_id, place_data in place_id_to_place_data_dict.items():
            miss_data = {
                'licno':licno,
                'place_id':place_data['place_id'],
                'name_tc':fehd['SS_TC'],
                'place_name_tc':place_data['place_tc']['result']['name'],
                'name_en':fehd['SS_EN'],
                'place_name_en':place_data['place_en']['result']['name'],
                'adr_tc':geocode_json['adr_tc'],
                'place_adr_tc':place_data['place_tc']['result']['formatted_address'],
                'adr_en':geocode_json['adr_en'],
                'place_adr_en':place_data['place_en']['result']['formatted_address'],
            }
            miss_data_list.append(miss_data)
            
miss_path = os.path.join(_utils.s03_merge_path_root,'miss.csv')
_utils.write_csv(miss_path,miss_data_list,['licno','place_id','name_tc','place_name_tc','name_en','place_name_en','adr_tc','place_adr_tc','adr_en','place_adr_en'])
