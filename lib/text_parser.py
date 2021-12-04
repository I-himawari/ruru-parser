
def talk_parser(talk):
    word_type = None
    player_name = None
    talk_message = None
    log_index = None
    player_talk = talk.find('td', class_='cn')  # プレイヤー発言
    gm_talk = talk.find('td', class_='cng')  # GM発言
    spectator_talk = talk.find('td', class_='cnw')  # 観戦者
    rip_talk = talk.find('td', class_='cnd')  # 霊界発言

    # プレイヤー発言
    if player_talk:
        talk_message = remove_html_tags(talk.find('td', class_='cc'))

        # 空要素の場合はスキップする
        if len(talk_message) == 0:
            return None

        # 狼の独り言検知
        word_type = 'night'
        if '<span class="end">の独り言</span>' in str(player_talk):
            word_type = 'whisper'
        elif '⑮' in str(talk):
            word_type = 'before15'
        player_name = remove_html_tags(player_talk).replace('の独り言', '')

        log_index_base = talk.find('span', class_='name'), talk.find('td', class_='cn')
        if log_index_base[1] is not None:
            index_result = str(log_index_base[1]).replace(str(log_index_base[1].span), '')
            log_index = remove_html_tags(index_result)  # .strip()

    # GM発言
    elif gm_talk:
        word_type = 'gm'
        player_name, talk_message = get_double_td(talk)

    # 観戦発言
    elif spectator_talk:
        word_type = "spectator"
        player_name, talk_message = get_double_td(talk)

    # 霊界発言
    elif rip_talk:
        word_type = 'rip'
        player_name, talk_message = get_double_td(talk)
    

    # 実行値の格納
    move_data = {
        'name': player_name,
        'text': talk_message,
        'type': word_type,
        'index': log_index,
    }
    return move_data