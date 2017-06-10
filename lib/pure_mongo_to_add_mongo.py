import pymongo
import json
import os
import sys
import time
import copy
import re
from pprint import pprint

"""
格納されたMongoのデータを、使いたい形に変形させる
"""
"""
TODOLIST
・全ログ取得への対応
"""

# MongoDBの立ち上げ
os.system('sudo service mongod start')

# MongoDBの接続及び仮想環境の作成
client = pymongo.MongoClient()
automata_db = client['PretaAutomata']
a = automata_db['PretaAutomata']
add_a = automata_db['AddPretaAutomata']  # 元データを加工したものをぶっ込むフィールド
add_a.remove()  # AddPretaAutomataの初期化


def virtual_role():
    """
    潜伏占いのチェックをする
    :return:
    """

def day_cutter(log, target_day, noon=True):
    """
    指定された日時でカットする
    :param log: dict
    :param day: int
    :param noon: bool
    :return: カットしたログかNone
    """
    noon_or_night = 'noon' if noon else 'night'
    day_param = 'day_%d_%s' % (target_day, noon_or_night)
    if day_param in log:
        return log[day_param]
    else:
        None

def add_player_talk_id(day_log, player_list):
    """
    プレイヤーごとに発言IDを割り振る。
    :param day_log: 1日単位のログ
    :param player_list: プレイヤーリスト
    :return: 直接書き換える
    """
    player_list_count = dict()
    for player in player_list:
        player_name = player['name']
        player_list_count[player_name] = 1

    for talk in day_log:
        talk['player_talk_id'] = player_list_count[talk['name']]
        player_list_count[talk['name']] += 1


def day_log_add_id(day_log):
    """
    その日のログにID(day_id)を割り振る
    :param day_log:
    :return:
    """
    for v in range(len(day_log)):
        day_log[v]['day_id'] = v + 1
    return day_log


def get_virtual_role(v, target_day=None, noon=True):
    """
    プレイヤーの役職名を仮想役職名に変換する
    :param v: IDを割り振られたログ全部
    :return: v['player']に'virtual_role'を追加し、v['target_day']を修正した値。
    """

    def virtual_role_check(t, p):
        """
        仮想役職チェック（全部の判定を下す）

        target_dayが指定されていない場合は、全ログから取得する。

        仮想占い判定が下るのは、以下の条件を満たした時。
        1　非村人
        2　1発言目と2発言目で占い正規表現チェッカーに引っかがった時。
        3（未実装）　占いCOがコピペではない時

        仮想霊能判定は未実装

        仮想狩人判定は未実装
        """
        if p['role'] == '村人':
            return '村人'

        # 最初の2発言のみ抽出する残りの発言まで含めると、ノイズが加わる可能性が高まる為
        t.sort(key=lambda x: x['player_talk_id'])
        if len(t) >= 2:
            t = t[0:2]
        seer_regex_checker_base = r'^\s?(占い|うらない)(CO|ＣＯ)( |　)?.+(○|●|村人|人狼)'
        seer_regex_checker = re.compile(seer_regex_checker_base)

        for talk in t:
            if seer_regex_checker.match(talk['text']):
                return '占い師'

        return '村人'

    # プレイヤーごとにログを取得する
    for player in v['player']:
        # 名前の取得をし、そのプレイヤーのログを取得する。
        talk_list = [talk for talk in v['target_log'] if talk['name'] == player['name']]
        # print(player['name'], talk_list)

        # そのプレイヤーのログから、仮想役職を取得する。
        player['virtual_role'] = virtual_role_check(talk_list, player)

    return v['player']


def main_log_set():
    """
    メインの統計処理をあれこれする所
    """

    # 設定変数
    target_vill_number = 17
    target_day = 2  # 取得したい日時。指定しない場合はNone
    target_log_type = 'talk'
    target_virtual_role = True
    # 設定変数終わり

    d = a.find({'meta.villagers_number': str(target_vill_number)})

    print('ログをMongoDBに出力中')
    for v in d:
        # プレイヤー数が規定以外の場合は返す
        if len(v['player']) != target_vill_number:
            continue

        # 取得したいログだけ、target_logに挿入する。
        if target_day:
            # データを取りたい日時のみ取得する。もし存在しない日時の場合はこの後の処理をしない。
            today_data = day_cutter(v['log'], target_day=target_day, noon=True)
            if today_data is None:
                continue
            v['target_log'] = day_log_add_id(today_data)  # ログに日ごとのIDを割り振る

        # 取得したいログ形式だけ、target_logに挿入する。
        if target_log_type:
            target_log = list()
            [target_log.append(talk) for talk in v['target_log'] if talk['type'] == target_log_type]
            v['target_log'] = target_log

        # プレイヤーごとに発言IDを割り振る。（このメソッドはvのdataをそのまま書き換える）。
        add_player_talk_id(day_log=v['target_log'], player_list=v['player'])

        # もし全ログ取得をする場合、ここでPandasが扱いやすい形に変換する。
        # 今回は全ログ取得はまだしないのでスキップする。

        # その日の振る舞いから、仮想役職を取得する。
        if target_virtual_role:
            v['player'] = get_virtual_role(v, target_day=target_day, noon=True)

        # 余計なデータを消す
        del v['log']

        # ログをMongoに挿入する
        # pprint(v)
        add_a.insert_one(v)

    print('出力完了')

if __name__ == '__main__':
    main_log_set()
