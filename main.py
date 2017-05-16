# るる鯖の情報をパースしてdictで返す
import requests
from bs4 import BeautifulSoup
import re


def ruru_parser(url):
    """
    るる鯖のログを取得し、dictで返す
    urlで指定する
    """
    def meta_parser(s):
        # るるスレのヘッダーを取得する
        header = str(s.find('div', class_='d11'))

        villagers_name_regex = r'「.*」'
        villagers_number_regex = r'参加:..?名'
        role_pattern_regex = r'\[配役.\]'  # 配役パターン

        meta_data = dict()

        # 参加人数の取得
        meta_data['villagers_name'] = re.search(villagers_name_regex, header).group().lstrip('「').rstrip('」')
        meta_data['villagers_number'] = re.search(villagers_number_regex, header).group()
        meta_data['role_pattern'] = re.search(role_pattern_regex, header).group()

        print(meta_data)

        return meta_data

    # htmlを取得する
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')

    # metaの処理をする
    ruru_dict = {}
    meta_parser(soup)


ruru_parser('https://ruru-jinro.net/log5/log419460.html')
