import pandas as pd
import numpy as np
import pymongo
import json
import os
import sys
import time
import copy
import re
from pprint import pprint

"""
やる予定の統計
2日の仮定村人発言の、役職ごとの発言傾向の違い（役職ずつ別々のプロットを取る予定）
"""

# MongoDBの立ち上げ
os.system('sudo service mongod start')

# MongoDBの接続及び仮想環境の作成
client = pymongo.MongoClient()
automata_db = client['PretaAutomata']
a = automata_db['PretaAutomata']
add_a = automata_db['AddPretaAutomata']  # 元データを加工したものをぶっ込むフィールド

# 取得したい日時のログを収録する。
d = add_a.find()

if __name__ == '__main__':
    talk_list = list()  # 発言データが色々投げ込まれるゴミ箱

    print('データ取得開始')
    count = 0
    # role_pattern = dict()
    for v in d:
        # プレイヤー数が規定に満たない場合、統計の対象としない。
        if len(v['player']) != 17:
            continue

        count += 1
        # 暫定村人の発言のみ取得する
        # 暫定村人リストを作成する
        vill_list = [player['name'] for player in v['player'] if player['virtual_role'] == '村人']

        # 暫定村人のログのみ取得した後、それぞれの役職のデータを入れる。
        # roleを入れるのはpure_mongo_to_add_mongo.pyの方で実装しなおす
        for t_log in v['target_log']:
            if t_log['name'] not in vill_list:
                continue
            t_log['role'] = [player['role'] for player in v['player'] if player['name'] == t_log['name']][0]
            talk_list.append(t_log)

    print('データ取得完了。合計%d村のデータを取得' % count)


    if not os.path.exists('../cache/'):
        os.mkdir('../cache/')
    f = open('../cache/cache', 'w')
    json_data = json.dumps(
        talk_list,
        sort_keys=True, ensure_ascii=False, indent=2
    )
    f.write(json_data)
    f.close()

    # cache_metaとかに色々なデータを書いておきたい。取得したデータの数とか。
