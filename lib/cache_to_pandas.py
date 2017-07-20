# キャッシュのデータをpandasであれこれする
from datetime import datetime
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
import matplotlib.pyplot as plt
import matplotlib
import sys
import codecs
from janome.tokenizer import Tokenizer

# 形態素解析のセッティング
t = Tokenizer()

# グラフの出力を日本語に指定する。
font = {'family' : 'TakaoGothic'}
matplotlib.rc('font', **font)

# MongoDBの立ち上げ
os.system('sudo service mongod start')

# MongoDBの仮想環境への接続
client = pymongo.MongoClient()
automata_db = client['PretaAutomata']
add_a = automata_db['AddPretaAutomata']

# 取得したい日時のログを収録する。
dt = datetime(2015, 4, 1, 12, 30, 59, 0).timestamp()
d = add_a.find({'meta.timestamp': {'$gte': dt}})

talk_list = list()  # 発言データが色々投げ込まれるゴミ箱

# 初期設定おわり
# 後は適当にやって、どうぞ。
# 以降サンプル
for v in d:
    wolf_list = [player for player in v['player'] if player['role'] == '人狼']
    # COパターンの作成
    seer = len([pl for pl in wolf_list if pl['virtual_role'] == '占い師'])
    mid = len([pl for pl in wolf_list if pl['virtual_role'] == '霊能者'])
    co_pattern = '%s-%s' % (seer, mid)
    append_data = (co_pattern, v['meta']['victory'])
    # 勝利役職の挿入
    talk_list.append(append_data)  # もはやtalk_listではない

df = pd.read_json(talk_list)

def get_role_dict(df_def, role, hinshi):
    df_def = df_def[df_def.role == role]
    talk_dict = dict()
    count = 0
    for talk_lists in df_def.text:
        result = t.tokenize(talk_lists)
        for mrph in result:
            talk_message = mrph.surface
            if not mrph.part_of_speech.split(',')[0] == hinshi:
                continue
            if talk_message in talk_dict:
                talk_dict[talk_message] += 1
            else:
                talk_dict[talk_message] = 1
        count += 1
        print(count, df_def.count().text)
    return talk_dict


# 狼の発言を形態素解析にかける
wolf_talk_dict = get_role_dict(df, '人狼', '名詞')

# pd.Series(wolf_talk_dict).sort_values(ascending=False).head(100).plot.bar()
# 村の発言を形態素解析にかける
vill_talk_dict = get_role_dict(df, '村人', '名詞')

vs = pd.Series(vill_talk_dict).sort_values(ascending=False).head(100)
ws = pd.Series(wolf_talk_dict).sort_values(ascending=False).head(100)

vs = vs.to_frame()
ws = ws.to_frame()

vs.columns=['vill_count']
ws.columns=['wolf_count']

talk_count = ws.sum(axis=0)[0] / vs.sum(axis=0)[0]
for i in range(vs.count()[0]):
    vs['vill_count'][i] = int(vs['vill_count'][i] * talk_count)

vs.join(ws, how='outer').plot.bar()
plt.show()
"""
for talk_lists in wolf_df.text:
    try:
        result = jumanpp.analysis(talk_lists)
        for mrph in result.mrph_list():
            talk_message = format(mrph.midasi)
            if talk_message in wolf_talk_dict:
                wolf_talk_dict[talk_message] += 1
            else:
                wolf_talk_dict[talk_message] = 1
        count += 1
        print(count, wolf_df.count().text)
    except:
        print('ERROR!')


wolf_df = df[df.role == '村人']
vill_talk_dict = dict()
count = 0
for talk_lists in wolf_df.text:
    try:
        result = jumanpp.analysis(talk_lists)
        for mrph in result.mrph_list():
            talk_message = format(mrph.midasi)
            if talk_message in vill_talk_dict:
                vill_talk_dict[talk_message] += 1
            else:
                vill_talk_dict[talk_message] = 1
        count += 1
        print(count, wolf_df.count().text)
    except:
        print('ERROR!')
"""


"""
# 最大発言数のカウントを取得する
vill = df[df['role'] == '村人']['player_talk_id'].value_counts(sort=False).sort_index().loc[df.index <= 10]
for v in vill.index.values[::-1]:
    for l in range(v-1):
        vill[l+1] = vill[l+1] - vill[v]


w = df[df['role'] == '人狼']['player_talk_id'].value_counts(sort=False).sort_index().loc[df.index <= 10]
for v in w.index.values[::-1]:
    for l in range(v-1):
        w[l+1] = w[l+1] - w[v]


plot_data = pd.concat([vill, w], axis=1)
plot_data.columns = ['villager', 'werewolf']

# 1000 / plot_data['villager'].sum()
# 正規化する
villager_sum = plot_data['villager'].sum()
for v in plot_data['villager'].index:
    plot_data['villager'][v] = plot_data['villager'][v] * 1000 / villager_sum


werewolf_sum = plot_data['werewolf'].sum()
for v in plot_data['werewolf'].index:
    plot_data['werewolf'][v] = plot_data['werewolf'][v] * 1000 / werewolf_sum

plot_data.plot.bar()
plt.show()
"""
