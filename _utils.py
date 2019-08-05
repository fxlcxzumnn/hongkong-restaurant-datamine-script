import json
import hashlib
import os

def write_json(data, fn):
    with open(fn,'w') as fout:
        json.dump(data,fout,sort_keys=True,indent=2)
        fout.write('\n')

def read_json(fn):
    with open(fn,'r') as fin:
        return json.load(fin)

def mkdirs(path):
    if not os.path.isdir(path):
        os.makedirs(path)

def md5(s):
    m = hashlib.md5()
    m.update(s.encode('utf8'))
    return m.hexdigest()

def get_geocode_restaurant_path(licno):
    licno_md5 = md5(licno)
    restaurant_path = os.path.join(
        geocode_path_root,
        licno_md5[0],
        licno_md5[1],
        licno_md5[2],
        licno
    )
    return restaurant_path

def get_s02_place_path(place_id):
    key_md5 = md5(place_id)
    ret = os.path.join(
        s02_place_path_root,
        key_md5[0],
        key_md5[1],
        key_md5[2],
        key_md5
    )
    return ret

def get_s03_merge_path(licno):
    licno_md5 = md5(licno)
    ret = os.path.join(
        s03_merge_path_root,
        licno_md5[0],
        licno_md5[1],
        licno_md5[2],
        licno
    )
    return ret

def now_ts():
    return datetime.datetime.now().timestamp()

conf_file = 'conf.json'
conf = read_json(conf_file)
data_path = conf['data_path']
s00_fehd_path = os.path.join(data_path,'work','00_fehd','output.json')
geocode_path_root = os.path.join(data_path,'work','01_geocode')
s02_place_path_root = os.path.join(data_path,'work','02_place')
s03_merge_path_root = os.path.join(data_path,'work','03_merge')
