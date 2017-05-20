#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re


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
        villagers_number_regex = r'(参加:|定員：)..?名'
        role_pattern_regex = r'(\[配役.\]|役職\[.\])'  # 配役パターン
        meta_data = dict()

        # 村名の取得
        print(header)
        meta_data['villagers_name'] = re.search(villagers_name_regex, header).group().lstrip('「').rstrip('」')

        # 参加人数の取得
        villagers_number = re.search(villagers_number_regex, header).group()
        meta_data['villagers_number'] = re.search(r'[0-9][0-9]?', villagers_number).group()

        # 配役パターンの取得
        role_pattern = re.search(role_pattern_regex, header).group()
        meta_data['role_pattern'] = re.search(r'(A|B|C|D)', role_pattern).group()

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
                # spanタグの時間タグを取得してしまう事がある為、もし取得していた場合はずらす
                if role_data != [] and len(role_data) == 1:
                    role_list.append(str(role_data[0].text).replace('\u3000', ''))
                elif len(role_data) == 2:
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

    def main_text_parser(s):
        day_list = s.find_all('div', class_='d12151')

        # ログの長さから、ログ展開を推測し、分析する
        # 終了後と初日昼（開始前）の存在は確定とする
        for v in reversed(day_list):
            pass
        pass

    # ローカルが指定されている場合は、ローカルのhtmlを取得する
    if local_address:
        get_local_log = open(local_address).read()
        soup = BeautifulSoup(get_local_log, 'lxml')

    # URLが指定されている場合はURL先のHTMLを取得する
    else:
        get_request = requests.get(url)
        soup = BeautifulSoup(get_request.text, 'lxml')

    # metaの処理をする
    ruru_dict = dict()
    ruru_dict['meta'] = meta_parser(soup)
    ruru_dict['player'] = player_parser(soup)
    main_text_parser(soup)

    return ruru_dict


if __name__ == '__main__':
    ruru_parser(local_address='../log/105000.html')
    ruru_parser(url='https://ruru-jinro.net/log5/log419460.html')
