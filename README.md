# ruru-parser
るる鯖の情報→（Python→Go（予定））→覚者ログ形式（JSON）→MongoDB→Python

# 開発環境の切り替え
source activate ruru-parser

# 将来的にする予定の内容
  * パーサ部分をGoで書き直し

# 統計分析箇所（覚者のオートマタの箇所）の仕様
  * MongoDBに格納されたデータをコピーする。
  * 推測役職と本役職の二段構えで運用する。
  * 推測役職でデータにfilterをかけ、本役職ごとの統計データを得るって感じの運用方法をしたい。

# MongoDBのデータ情報
  * DB名: PretaAutomata
  * コレクション名: PretaAutomata
