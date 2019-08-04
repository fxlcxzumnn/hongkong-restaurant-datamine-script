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
