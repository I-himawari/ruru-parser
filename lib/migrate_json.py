# JSONのデータをMongoDBに格納する

import pymongo
import json
import os
import sys
import re
from bs4 import BeautifulSoup


files = os.listdir('../json/')
count = 0
for file in files:
    try:
        file_name = '../json/%s' % file
        get_json = json.load(open(file_name))

        # バージョン未指定（最初期バージョン）の場合のパッチ
        if not 'version' in get_json['meta']: 
            # ログの読み込み
            local_address='../log/%s.html' % file.split('.')[0]
            get_local_log = open(local_address).read()
            s = BeautifulSoup(get_local_log, 'lxml')

            get_json['meta']['version'] = '0.11'
            
            victory_data = str(s.find('span', class_='result'))
            victory_data = re.sub('<[^<]+?>', '', victory_data)
            victory_pattern = (
                ('「村　人」陣営の勝利です！！', 'vill'),
                ('「人　狼」陣営の勝利です！！', 'wolf'),
                ('「妖　狐」陣営の勝利です！！', 'fox'),
                ('引き分けです', 'draw'),  # 
            )
            victory_result = 'del'  # 廃村時
            for v in victory_pattern:
                if v[0] in victory_data:
                    victory_result = v[1]

            get_json['meta']['victory'] = victory_result

            # ログの出力
            f = open(file_name, 'w')
            f.write(json.dumps(get_json, sort_keys=True, ensure_ascii=False, indent=2))
            f.close()

        sys.stdout.write('\r%d' % count)
        sys.stdout.flush()
        count+=1
    except:
        print('ERROR')
