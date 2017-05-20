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


def download_ruru_log(ruru_number):
    """
    :param ruru_number: int
    :return:
    """
    save_path = '../log'

    # ファイルが無い場合は作成する
    if not os.path.exists(save_path):
        os.mkdir(save_path)

    file_pass = '../log/%s.html' % ruru_number  # 保存先のパス名
    log_number = (create_ruru_id(ruru_number))  # ログのID

    ruru_url = 'https://ruru-jinro.net/%s/log%d.html' % (log_number, ruru_number)
    try:
        urllib.request.urlretrieve(ruru_url, file_pass)
        print('GET %s' % ruru_url)
    except:
        print('ERROR %s' % ruru_url)
        pass

if __name__ == '__main__':
    for v in range(102212, 420000):
        download_ruru_log(v)
        time.sleep(1)

