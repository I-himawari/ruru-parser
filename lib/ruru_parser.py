#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime as dt
import os
import json


def ruru_old_log_checker(s):
    """
    古いログ形式ならTrue、そうでないならFalseを返す
    :param s:
    :return:
    """
    time_data_regex = r'[0-9]{4}\/[0-9]{2}\/[0-9]{2}\s[0-9]{2}:[0-9]{2}:[0-9]{2}'
    # るる鯖新ログ形式なら1つ目のdiv:d12150で時刻が取得可能。そうでないなら取得不可
    time_data = re.search(time_data_regex, str(s.find('div', class_='d12150')))
    return False if time_data else True


def ruru_parser(local_address=None, url=None):
    """
    るる鯖のログを取得し、dictで返す
    urlで指定する
    """
    def meta_parser(s):
        """
        るるスレのヘッダーを取得する
        s: soup
        """
        header = str(s.find('div', class_='d11'))

        villagers_name_regex = r'「.*」'
        villagers_number_regex = r'(参加:|定員：|定員:)..?名'
        role_pattern_regex = r'(\[配役.\]|役職\[.\])'  # 配役パターン
        time_data_regex = r'[0-9]{4}\/[0-9]{2}\/[0-9]{2}\s[0-9]{2}:[0-9]{2}:[0-9]{2}'
        meta_data = dict()

        # 村名の取得
        meta_data['villagers_name'] = re.search(villagers_name_regex, header).group().lstrip('「').rstrip('」')

        # 参加人数の取得
        villagers_number = re.search(villagers_number_regex, header).group()
        meta_data['villagers_number'] = re.search(r'[0-9][0-9]?', villagers_number).group()

        # 配役パターンの取得
        role_pattern = re.search(role_pattern_regex, header).group()
        meta_data['role_pattern'] = re.search(r'(A|B|C|D|Z)', role_pattern).group()

        # timestampの取得
        time_data = re.search(time_data_regex, str(s.find('div', class_='d12150')))  # るる鯖新ログ形式なら取得可
        if not time_data:
            time_data = re.search(time_data_regex, str(s.find_all('div', class_='d12150')[1]))

        meta_data['timestamp'] = int(dt.strptime(time_data.group(), '%Y/%m/%d %H:%M:%S').timestamp())
        meta_data['server_name'] = 'ruru'

        meta_data['version'] = '0.11'
        
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

        meta_data['victory'] = victory_result
        

        # 勝利役職の取得
        # 未実装

        return meta_data

    def player_parser(s):
        """
        プレイヤーの情報をパースして返す
        s: soup
        """
        player = s.find('table', class_='iconsmall').find_all('td')

        player_list = list()
        trip_list = list()
        role_list = list()

        # ログのタイプを選択する
        log_type = ['icon', 'player', 'icon', 'player', 'role', 'role', 'reset']
        now_log = 0

        # プレイヤーとロールの対応表を作る
        for v in player:
            if log_type[now_log] == 'player':
                # プレイヤー名を取得する
                player_data = v.find('span')
                if player_data is not None:
                    player_list.append(player_data.text)

                # トリップ名を取得する
                trip_data = re.search(r'【.*】', str(v))
                if trip_data is not None:
                    trip_list.append(trip_data.group().lstrip('【').rstrip('】').replace('<wbr>', ''))

            elif log_type[now_log] == 'role':
                role_data = v.find_all('span')
                #
                if role_data != [] and len(role_data) == 1:
                    role_list.append(str(role_data[0].text).replace('\u3000', ''))
                # spanタグの時間タグを取得してしまう事がある為、もし取得していた場合はずらす
                elif len(role_data) >= 2:
                    role_list.append(str(role_data[1].text).replace('\u3000', ''))
            now_log += 1
            if log_type[now_log] == 'reset':
                now_log = 0

        # コンバートする
        all_player_list = list()
        for v in range(len(player_list)):
            all_player_list.append({
                'name': player_list[v],
                'role': role_list[v],
                'trip': trip_list[v]
            })

        return all_player_list

    def main_text_parser(s, player_list={}):
        """
        主文をコンバートする
        :param s:BeautifleSoup
        :return:
        """
        day_list = s.find_all('div', class_='d12151')

        # ログの長さから、ログ展開を推測し、分析する
        # 終了後と初日昼（開始前）の存在は確定とする
        first_div = True  # 最初のdiv判定
        end_day = True  # 終了後判定
        old_log_type = ruru_old_log_checker(s)  # 旧ログ形式かチェクする
        now_day = None  # 現在の日数を取得する
        night_checkr = r'd12151 log_night'  # 夜チェッカー
        i = 0
        all_log_data = dict()  # 全ての発言ログを取得する変数
        for v in day_list:
            i += 1
            # print(v)
            # 旧ログの場合、最初のd12151はスキップする。
            if first_div:
                first_div = False
                if old_log_type:
                    continue

            # ログを取得する
            talks = v.find_all('tr')

            # 終了後のログの解析をする
            if end_day:
                end_day = False
                # 未実装

            # 開始前ログの解析をする
            elif i == len(day_list):
                # 未実装
                pass

            # ゲーム中のログ解析をする
            else:
                # ゲーム内日付を取得する
                now_date = (len(day_list) - 2 - i) // 2 + 2
                # 夜中
                if '<div class="d12151 log_night">' in str(v):
                    # 夜中のログ取得は未実装
                    # for talk in talks:
                    #     pass
                    pass

                # 日中
                else:
                    move_datas = list()
                    for talk in talks:
                        name, text = talk.find('span', class_='name'), talk.find('td', class_='cc')
                        # '投票時間になりました。時間内に処刑の対象を決定してください'

                        # 発言ログで、空ログではない場合の処理
                        if text and name:
                            # 独り言か否かのチェック
                            if '<span class="end">の独り言</span>' in str(talk):
                                log_type = 'soliloquence'
                            else:
                                log_type = 'talk'

                            name = str(name.get_text())  # re.sub(r'<?span.*>', '', str(name))
                            text = re.sub(r'<br/>', ' ', str(text))
                            text = re.sub('<[^<]+?>', '', text)
                            move_data = {
                                'name': name,
                                'text': text,
                                'type': log_type,
                            }
                            move_datas.append(move_data)

                        # 投票の場合の処理　未実装

                    move_datas.reverse()  # 取得ログを逆転させる
                    day_x_noon = 'day_%d_noon' % now_date
                    all_log_data[day_x_noon] = move_datas

        return all_log_data


    # ローカルが指定されている場合は、ローカルのhtmlを取得する
    if local_address:
        get_local_log = open(local_address).read()
        soup = BeautifulSoup(get_local_log, 'lxml')

    # URLが指定されている場合はURL先のHTMLを取得する
    else:
        get_request = requests.get(url)
        soup = BeautifulSoup(get_request.content, 'lxml')

    ruru_dict = dict()
    ruru_dict['meta'] = meta_parser(soup)
    ruru_dict['player'] = player_parser(soup)
    ruru_dict['log'] = main_text_parser(soup)

    return ruru_dict


if __name__ == '__main__':
    files = os.listdir('../log/')
    for file in files:
        # ファイルをパースし、失敗したら見なかった事にする
        try:
            write_file_name = '../json/%s' % file.split('.')[0] + '.json'
            if os.path.exists(write_file_name) and os.path.getsize(write_file_name) != 0:
                print('EXIST %s' % file)
            else:
                print('OPEN %s' % file)
                f = open(write_file_name, 'w')
                json_data = json.dumps(
                        ruru_parser(local_address='../log/%s' % file),
                        sort_keys=True, ensure_ascii=False, indent=2
                    )
                f.write(json_data)
                f.close()
        except:
            print('ERROR %s' % file)
