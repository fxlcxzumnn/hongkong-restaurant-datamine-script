import xml.etree.ElementTree as ET
import json
import os
import sys
import _utils

conf_file = 'conf.json'
conf = _utils.read_json(conf_file)

data_path = conf['data_path']

lang_to_lp_rest_path_dict = {}
lang_to_lp_rest_path_dict['EN'] = os.path.join(data_path,'input','LP_Restaurants_EN.XML')
lang_to_lp_rest_path_dict['TC'] = os.path.join(data_path,'input','LP_Restaurants_TC.XML')

licno_to_lp_dict = {}

def assign_lp_data(lp_data, lp, att):
    v = lp.find(att)
    if v is None: return
    v = v.text
    if v is None: v = ''
    if not att in lp_data:
        lp_data[att] = v
        return
    if lp_data[att] != v:
        print('WARNING: lp_data[att] != v, lp_data[att]={0}, v={1}'.format(lp_data[att],v))

def assign_lp_data_lang(lp_data, lp, att, lang):
    v = lp.find(att)
    if v is None: return
    v = v.text
    if v is None: v = ''
    key = '{att}_{lang}'.format(att=att,lang=lang)
    lp_data[key] = v

for lang, lp_rest_path in lang_to_lp_rest_path_dict.items():
    eletree = ET.ElementTree(file=lp_rest_path)
    for lp in eletree.iterfind('LPS/LP'):
        licno = lp.find('LICNO').text
        if licno not in licno_to_lp_dict: licno_to_lp_dict[licno] = {}
        lp_data = licno_to_lp_dict[licno]
        lp_data['LICNO'] = licno

        assign_lp_data(lp_data,lp,'TYPE')
        assign_lp_data(lp_data,lp,'DIST')
        assign_lp_data(lp_data,lp,'EXPDATE')
        assign_lp_data(lp_data,lp,'INFO')
        assign_lp_data_lang(lp_data,lp,'SS',lang)
        assign_lp_data_lang(lp_data,lp,'ADR',lang)

#print(json.dumps(licno_to_lp_dict,sort_keys=True,indent=2))

output_restaurant_list = []
licno_list = licno_to_lp_dict.keys()
licno_list = sorted(licno_list)
licno_list = list(licno_list)
for licno in licno_list:
    lp = licno_to_lp_dict[licno]
    output_restaurant_list.append(lp)

output_data = {}
output_data['restaurant_list'] = output_restaurant_list

output_path = os.path.join(data_path,'work','00_fehd','output.json')
_utils.write_json(output_data, output_path)
