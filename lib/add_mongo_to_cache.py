# MongoDBの割り出し結果をキャッシュに保存する

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
from datetime import datetime

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
dt = datetime(2016, 10, 1, 12, 30, 59, 0).timestamp()
d = add_a.find({'meta.timestamp': {'$gte': dt}})


if __name__ == '__main__':
    talk_list = list()  # 発言データが色々投げ込まれるゴミ箱

    # 以降のソースコードは場合によって変更する可能性が高い。
    print('データ取得開始')
    count = 0
    for v in d:
        count += 1
        vill_list = [player['name'] for player in v['player'] if player['role'] == '人狼']

        # 指定暫定役職のログのみ取得した後、Pandasが処理しやすいように、発言ごとにそれぞれの役職のデータを入れる。
        # roleを入れるのはpure_mongo_to_add_mongo.pyの方で実装しなおしてもいいかも。
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
