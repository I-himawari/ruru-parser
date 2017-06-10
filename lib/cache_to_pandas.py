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

"""
やる予定の統計
・暫定村人の、役職ごとの発言回数の平均値
・（家に帰ってから）2日の仮定村人発言の、役職ごとの発言傾向の違い（役職ずつ別々のプロットを取る予定）

"""

if __name__ == '__main__':
    all_log = open('../cache/cache').read()  # キャッシュした全データ
    df = pd.read_json(all_log)
    df = df[df.role == '村人']
    del df['type']
    table = pd.pivot_table(
        df, index=[], columns=['_id'], aggfunc=np.sum)
    print(table)
