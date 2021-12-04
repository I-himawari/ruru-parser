# ruru-parser

るる鯖の情報→（Python→Go（予定））→覚者ログ形式（JSON）→MongoDB→Python

## 使い方

* log_getter.py  るる鯖ログを取得
* ruru_parser.py  JSONに変換
* json_to_mongo.py  JSONをMongoDBに格納
* pure_mongo_to_add_mongo.py  元データを条件ごとに切り割りする（例: 身内村の除外 取得配役の選択　など）

add_mongo_to_cacheとcache_to_pandasはJupyter

## 更新履歴

0.1 なんか作った
0.11 ログ解析結果を入れた（消した）
0.2 ようやく全ログ取得が出来るようになった