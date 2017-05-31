import urllib.request
import os
import os.path
import time


def create_ruru_id(ruru_number):
    """
    るる鯖のログID（logXなど）を作成する
    :param ruru_number: int
    :return:
    """
    log_number = int(ruru_number / 100000) + 1
    if log_number == 1:
        ruru_log_id = 'log'
    else:
        ruru_log_id = 'log%d' % log_number

    return ruru_log_id


def download_ruru_log(ruru_number, save_path='../log'):
    """
    指定されたるる鯖のナンバーのログを取得する。指定した場所にログがある場合は無を返す
    :param ruru_number: int
    :param save_path: str
    :return: bool
    """

    # ファイルが無い場合は作成する
    if not os.path.exists(save_path):
        os.mkdir(save_path)

    file_pass = '../log/%s.html' % ruru_number  # 保存先のパス名
    if os.path.isfile(file_pass):
        print('EXIST %s' % file_pass)
        return False

    log_number = (create_ruru_id(ruru_number))  # ログのID
    ruru_url = 'https://ruru-jinro.net/%s/log%d.html' % (log_number, ruru_number)
    try:
        urllib.request.urlretrieve(ruru_url, file_pass)
        print('GET %s' % ruru_url)
        return True
    except:
        print('ERROR %s' % ruru_url)
        return True

if __name__ == '__main__':
    for v in range(100000, 420000):
        if download_ruru_log(v):
            time.sleep(1)

