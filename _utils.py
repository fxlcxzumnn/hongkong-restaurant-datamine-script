import json
import hashlib
import os
import csv

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

def write_csv(fn,v_dict_list,col_name_list=None,sort_key_list=None):
    if col_name_list is None:
        assert(len(v_dict_list)>0)
        col_name_list = list(sorted(v_dict_list[0].keys()))
    if sort_key_list is not None:
        t_list = [ ( \
                    tuple(v_dict[c] for c in sort_key_list), \
                    tuple(v_dict[c] for c in col_name_list), \
                    v_dict, \
                    ) for v_dict in v_dict_list ]
        t_list = sorted(t_list)
        v_dict_list = [ t[2] for t in t_list ]
    with open(fn,'w') as fout:
        csv_out = csv.writer(fout)
        csv_out.writerow(col_name_list)
        for v_dict in v_dict_list:
            csv_out.writerow([v_dict[col_name] for col_name in col_name_list])

conf_file = 'conf.json'
conf = read_json(conf_file)
data_path = conf['data_path']
s00_fehd_path = os.path.join(data_path,'work','00_fehd','output.json')
geocode_path_root = os.path.join(data_path,'work','01_geocode')
s02_place_path_root = os.path.join(data_path,'work','02_place')
s03_merge_path_root = os.path.join(data_path,'work','03_merge')
