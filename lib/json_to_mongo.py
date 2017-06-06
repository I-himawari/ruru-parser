import pymongo
import json
import os
import sys

client = pymongo.MongoClient()
automata_db = client['PretaAutomata']
automata_col = automata_db['PretaAutomata']
automata_col.remove()
files = os.listdir('../json/')
count = 0
for file in files:
    try:
        file_name = '../json/%s' % file
        get_json = json.load(open(file_name))
        automata_col.insert_one(get_json)
        sys.stdout.write('\r%d' % count)
        sys.stdout.flush()
        count+=1
    except:
        print('ERROR')
