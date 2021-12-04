#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime as dt
import os
import json
import sys

# HTMLタグ消し
# 変更入るとややこしくなるので関数にまとめる
def remove_html_tags(text):
    return re.sub('<[^<]+?>', '', str(text))

def get_double_span(v, class_name):
    result = v.find_all('span', class_=class_name)
    one = remove_html_tags(result[0])
    two = remove_html_tags(result[1])
    return one, two

def get_double_td(v):
    result = v.find_all('td')
    one = remove_html_tags(result[0])
    two = remove_html_tags(result[1])
    return one, two

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
        role_pattern_regex = r'(\[配役.\]|役職\[.\])'  # 配役パターン
        time_data_regex = r'[0-9]{4}\/[0-9]{2}\/[0-9]{2}\s[0-9]{2}:[0-9]{2}:[0-9]{2}'
        meta_data = dict()

        # 村名の取得
        meta_data['villagers_name'] = re.search(villagers_name_regex, header).group().lstrip('「').rstrip('」')

        # 参加人数の取得
        # 定員と間違えがちだし、プレイヤー名のカウントを取ればいいので削除
        """
        villagers_number_regex = r'(参加:|定員：|定員:)..?名'
        villagers_number = re.search(villagers_number_regex, header).group()
        meta_data['villagers_number'] = re.search(r'[0-9][0-9]?', villagers_number).group()
        """

        # 配役パターンの取得
        role_pattern = re.search(role_pattern_regex, header)
        # 昔の村は配役パターンがない為スキップ
        if role_pattern:
            role_pattern = role_pattern.group()
            meta_data['role_pattern'] = re.search(r'(A|B|C|D|Z)', role_pattern).group()
        else:
            meta_data['role_pattern'] = None

        # timestampの取得
        time_data = re.search(time_data_regex, str(s.find('div', class_='d12150')))  # るる鯖新ログ形式なら取得可
        if not time_data:
            time_data = re.search(time_data_regex, str(s.find_all('div', class_='d12150')[1]))

        # 昔の村は日付情報が入っていない為、その場合はスキップする
        if time_data:
            meta_data['timestamp'] = int(dt.strptime(time_data.group(), '%Y/%m/%d %H:%M:%S').timestamp())
        else:
            meta_data['timestamp'] = 0

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
        # player = s.find('table', class_='iconsmall').find_all('td')
        player = s.find('div', class_='d1221').find_all('td')

        player_list = list()
        trip_list = list()
        role_list = list()

        # ログのタイプを選択する
        # るる鯖ログの仕様上、この順番でログ取得をする必要性がある
        log_type = ['icon', 'player', 'icon', 'player', 'role', 'role', 'reset']
        role_type = ["村人", "人狼", "占い師", "霊能", "狂人", "狩人", "共有", "妖狐", "狂信者", "背徳者", "猫又", "決定前"]
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
                # 役職にヒットするまでループする
                kari_role_data = v.find_all('span')
                if len(kari_role_data):
                    hit_role = False
                    for v in kari_role_data:
                        kari_role_str = str(v.text).replace('\u3000', '')
                        # print(kari_role_str)
                        if kari_role_str in role_type:
                            role_list.append(kari_role_str)
                            hit_role = True
                            break
                    
                    # 役職検知ミスは重大なエラーなので検出する
                    if not hit_role:
                        raise ValueError("ヒットする役職名がありません")

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
        all_log_data = list()  # 全ての発言ログを取得する変数
        # all_log_data = dict()  # 全ての発言ログを取得する変数
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

            # 取得ログを逆転させる
            # 投票ログ管理とかがやりやすくなる
            talks.reverse() 

            # 終了後のログの解析をする
            # tr:nth-child(12) > .cv
            # tr:nth-child(21) > .cv
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
                    """
                    tdクラスごとの発言傾向
                    cn プレイヤー
                    cnw 観戦者
                    cng GM発言
                    ca 役職
                    <tr><td class="ca" colspan="2"><span class="fortune">「<span class="name">せと</span>」さんは「<span class="name">オリオリオ</span>」さんを占いました　結果：<span class="oc00">【村　人】</span></span></td></tr>
                    <tr><td class="ca" colspan="2"><span class="wolf">「<span class="name">モハメドりあ</span>」さんは「<span class="name">第一犠牲者</span>」さんを噛みました</span></td></tr> 
                    <tr><td class="ca" colspan="2"><span class="hunter">「<span class="name">オリオリオ</span>」さんは「<span class="name">せと</span>」さんを護衛しました</span></td></tr>      
                    """
                    """
                    spanクラスごとの役職（別になくてもいいや。狼の場合は独り言は入れるべきだけど）
                    <span class="turquoise oc02 name">せと</span>
                    占い
                    <span class="fox">ぶwwww</span>
                    狐
                    <span class="wolf">
                    <span class="joint"> 共有

                    """
                    move_datas = list()
                    action_datas = list()
                    death_target = None

                    for talk in talks:
                        word_type = None
                        player_name = None
                        talk_message = None
                        player_talk = talk.find('td', class_='cn')  # プレイヤー発言
                        gm_talk = talk.find('td', class_='cng')  # GM発言
                        acction_talk = talk.find('td', class_='ca')  # 役職実行
                        spectator_talk = talk.find('td', class_='cnw')  # 観戦者
                        rip_talk = talk.find('td', class_='cnd')  # 霊界発言
                        game_message = talk.find('td', class_='cs')  # ゲームシステムメッセージ

                        # プレイヤー発言
                        if player_talk:
                            talk_message = remove_html_tags(talk.find('td', class_='cc'))

                            # 空要素の場合はスキップする
                            if len(talk_message) == 0:
                                continue

                            # 狼の独り言検知
                            word_type = 'night'
                            if '<span class="end">の独り言</span>' in str(player_talk):
                                word_type = 'whisper'
                            player_name = remove_html_tags(player_talk).replace('の独り言', '')
                    
                        # GM発言
                        elif gm_talk:
                            word_type = 'gm'
                            player_name, talk_message = get_double_td(talk)
                            """
                            # 動作が怪しかったらこっちに戻してもいい
                            player_name = talk.find_all('span', class_='gm')[0]
                            player_name = remove_html_tags(player_name)
                            talk_message = talk.find_all('span', class_='gm')[1]
                            talk_message = remove_html_tags(talk_message)
                            """
                        
                        # 役職実行
                        elif acction_talk:
                            talk_str = str(talk)
                            action_role = None
                            # !!! 役職名（英語）は後で考える
                            if '<span class="fortune">' in talk_str:
                                action_role = '占い師'
                            elif '<span class="wolf">' in talk_str:
                                action_role = '人狼'
                            elif '<span class="hunter">' in talk_str:
                                action_role = '狩人'
                            else:
                                print(talk)
                                raise ValueError('不明役職')

                            from_name, to_name = get_double_span(talk, 'name')
                            action_datas.append({
                                "role": action_role,
                                "from_name": from_name,
                                "to_name": to_name,
                            })
                            # 役職実行は発言じゃないのでcontinueする
                            continue

                        elif spectator_talk:
                            word_type = "spectator"
                            player_name, talk_message = get_double_td(talk)

                        elif rip_talk:
                            word_type = 'rip'
                            player_name, talk_message = get_double_td(talk)

                        # ゲームメッセージなど
                        elif game_message:
                            # print(talk)
                            # 処刑
                            if '<span class="death">' in str(talk):
                                death_target = remove_html_tags(str(talk.find('span', class_='name')))
                            continue

                        # その他
                        else:
                            print(talk)
                            raise ValueError('ちょっと怪しい')

                        if player_name is None:
                            print(talk)
                            raise ValueError('おかしな夜会話')

                        # 実行値の格納
                        move_data = {
                            'name': player_name,
                            'text': talk_message,
                            'type': word_type,
                        }
                        move_datas.append(move_data)

                    log_data = {
                        "day": now_date,
                        "state": "night",
                        "log": move_datas,
                        'actions': action_datas,
                        'vote_death': death_target,
                    }
                    all_log_data.append(log_data)

                # 日中
                else:
                    move_datas = list()
                    vote_datas = list()
                    vote_count = 0
                    for talk in talks:
                        vote = talk.find('td', class_='cv')
                        # 投票
                        if vote:
                            vote_count += 1
                            vote_data = list()
                            for v in vote.find_all('tr'):
                                b = v.find_all('span')
                                vote_data.append({'from': remove_html_tags(str(b[0])), 'to': remove_html_tags(str(b[1]))})
                            vote_datas.append({'count': vote_count, 'data': vote_data})
                            continue

                        name, text = talk.find('span', class_='name'), talk.find('td', class_='cc')
                        # '投票時間になりました。時間内に処刑の対象を決定してください'
                        # 発言ログで、空ログではない場合の処理
                        if text and name:
                            # 独り言か否かのチェック
                            # !!! 霊界発言チェックも必要だこれ
                            log_index = None
                            if '<span class="end">の独り言</span>' in str(talk):
                                log_type = 'soliloquence'
                            elif '<td class="ccd">' in str(talk):
                                log_type = 'ghost'
                            elif '⑮' in str(talk):
                                log_type = 'before15'
                            else:
                                log_type = 'talk'
                                
                                log_index_base = talk.find('span', class_='name'), talk.find('td', class_='cn')
                                if log_index_base[1] is not None:
                                    index_result = str(log_index_base[1]).replace(str(log_index_base[1].span), '')
                                    log_index = remove_html_tags(index_result)  # .strip()


                            name = str(name.get_text())  # re.sub(r'<?span.*>', '', str(name))
                            text = re.sub(r'<br/>', ' ', str(text))
                            text = re.sub('<[^<]+?>', '', text)
                            move_data = {
                                'name': name,
                                'text': text,
                                'type': log_type,
                                'index': log_index,
                            }
                            move_datas.append(move_data)
                            continue

                        print(talk)



                    # 要素名がころころ変わると取得しにくいので"day", "state"で指定させることにした
                    log_data = {
                        "day": now_date,
                        "state": "noon",
                        "log": move_datas,
                        'vote': vote_datas,
                    }
                    all_log_data.append(log_data)

        return all_log_data


    # ローカルが指定されている場合は、ローカルのhtmlを取得する
    if local_address:
        get_local_log = open(local_address, 'r', encoding='utf-8').read()
        soup = BeautifulSoup(get_local_log, 'lxml')

    # URLが指定されている場合はURL先のHTMLを取得する
    else:
        get_request = requests.get(url)
        soup = BeautifulSoup(get_request.content, 'lxml')

    ruru_dict = dict()
    ruru_dict['meta'] = meta_parser(soup)
    ruru_dict['player'] = player_parser(soup)
    ruru_dict['meta']['villagers_number'] = len(ruru_dict['player'])
    ruru_dict['log'] = main_text_parser(soup)

    return ruru_dict


def log_number_to_json(log_number, test_mode=False):
    save_path = '../json'
    write_file_name = f'{save_path}/{log_number}.json'
    
    # ファイルが無い場合は作成する
    if not os.path.exists(save_path):
        os.mkdir(save_path)

    if os.path.exists(write_file_name) and os.path.getsize(write_file_name) != 0 and not test_mode:
        print('EXIST %d' % log_number)
    else:
        print('OPEN %d' % log_number)
        f = open(write_file_name, 'w', encoding='utf-8')
        json_data = json.dumps(
                ruru_parser(local_address='../log/%d.html' % log_number ),
                sort_keys=True, ensure_ascii=False, indent=2
            )
        f.write(json_data)
        f.close()

if __name__ == '__main__':
    args = sys.argv

    if len(args) <= 1:
        files = os.listdir('../log/')
        for file in files:
            log_number_to_json(int(file.split('.')[0]))
            """
            # ファイルをパースし、失敗したら見なかった事にする
            # jsonディレクトリが必要。処理はgetの方にあった。
            # try:
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
            # except:
            #     print('ERROR %s' % file)
            """
    else:
        log_number_to_json(int(args[1]), test_mode=True)