# 今回使用しているJSONの形式
以下の形式（yaml）をJSONで書きなおしたもの

```yaml
meta:
  server: サーバのタイプ
  villagers_name: 村名
  villagers_number: プレイヤー数
  role_type: 配役タイプ（るる鯖基準。わかめて鯖の形式は別途検討）
  timestamp: 村のタイムスタンプ
  version: パーサのバージョン
  victory: 勝利陣営（vill, wolf, fox, draw, del　等。英語名）

player:
  name: 名前
  role: 役職名（村人、占い師、霊能者、共有者、狩人、人狼、狂人、妖狐　等。日本語名）
  trip: トリップ名

text:
  日数:
    noon(昼時間):
      name: プレイヤー名
      type: 行動タイプ（発言とか役職実行とか）（るる鯖の場合は、発言・投票・霊界会話・狼会話・共有会話・独り言・処刑・朝死体・占い・噛み・護衛）
      target: 対象ターゲット
      text: 発言の場合は本文

    night(夜時間):
      name: プレイヤー名
      type: 行動タイプ（発言とか役職実行とか）（るる鯖の場合は、発言・投票・霊界会話・狼会話・共有会話・独り言・処刑・朝死体・占い・噛み・護衛）
      target: 対象ターゲット
      text: 発言の場合は本文
```