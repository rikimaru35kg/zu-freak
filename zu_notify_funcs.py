import time
import datetime as dt
import traceback

import requests
import keyring
import cv2

import const
import line_notify
import get_weather
import get_traffic
# import send_pushbullet as spb
import play_sound as play


def zu_notify(t_now, frame, user):
    """Send LINE message
    
    Args:
        t_now (datetime): current time
        frame (np.ndarray): Image to be sent
    """
    message = f"""{t_now.strftime("%Y/%m/%d %H:%M:%S")}
    ズーカメラで動きが検知されました。

    現在のズー
    {keyring.get_password('zu', 'zu1')}

    現在＋過去のズー
    {keyring.get_password('zu', 'zu2')}"""

    cv2.imwrite('zu.png', frame)
    line_notify.send_line(message, 'zu.png', user)

    # spb.send_pushbullet('ズーだよ', '動いたよ')

    play.play_sound('./audio')


def zu_sleep():
    t_now = dt.datetime.now()

    message = f"""{t_now.strftime("%Y/%m/%d %H:%M:%S")}
    今日も一日お疲れ様でした。
    ズーカメラは明日の朝{const.TIME_START}時までお休みします。"""
    line_notify.send_line(message, user=const.USER, stamp=True)

    # sleep until TIME_START
    time_start = dt.datetime(t_now.year, t_now.month, t_now.day,
                                    const.TIME_START, t_now.minute, t_now.second)
    t_delta = time_start + dt.timedelta(days=1) - t_now
    time.sleep(t_delta.seconds)


def zu_weather():
    txt = f'\n厚木市のこれからの天気だワン\n{get_weather.get_weather("厚木市")}'
    line_notify.send_line(txt, user=const.USER)


def zu_traffic(direction='down'):
    jam = get_traffic.get_traffic(direction)
    _str = '下り' if direction == 'down' else '上り'
    if jam == '':
        txt = f'\n今は東名{_str}に渋滞は無いみたいだワン'
    else:
        txt = f'\n東名{_str}に渋滞が発生しているワン\n{jam}'
    line_notify.send_line(txt, user=const.USER, stamp=True)


def zu_holiday():
    """Send holiday information by LINE"""
    try:
        now = dt.datetime.now()
        year = now.year
        cw_this = now.isocalendar().week
        cw_next = (now + dt.timedelta(weeks=1)).isocalendar().week

        holidays = []
        for y in [year, year + 1]:
            url = 'https://api.national-holidays.jp/' + str(y)
            res = requests.get(url)
            if type(res.json()) is list:
                holidays += res.json()
                # [NOTE] ---------------------------------
                # If no information is stored on the above url,
                # {'error': 'not found'} is returned.
                # Normally, [{'date': '-'}, {'date': '-'}, ...]
                # is returned. (list is returned normally)
                # ----------------------------------------

        h_thisweek = []
        for holiday in holidays:
            if 'date' not in holiday.keys():
                continue
                # [NOTE] ---------------------------
                # Just in case there is not 'date' key
                # ----------------------------------
            _year = dt.datetime.strptime(holiday['date'], '%Y-%m-%d').year
            _cw = dt.datetime.strptime(holiday['date'], '%Y-%m-%d').isocalendar().week
            if ( ( (_year == year) and
                (_cw == cw_this)) or
                ( (_year == year) and
                (_cw == cw_next)) or
                ( (_year == year + 1) and
                (_cw == cw_next))):
                h_thisweek.append(holiday)

        if len(h_thisweek) > 0:
            message = '今週と来週の祝日情報だワン'
            for d in h_thisweek:
                message += f'\n{d["date"]}: {d["name"]}({d["type"]})'
            
            line_notify.send_line(message, user=const.USER, stamp=True)
    except:
        print('-------------------------------------------')
        print(f'Error: {dt.datetime.now().strftime("%Y/%m/%d-%H:%M:%S")}')
        print('Location: zu_holiday() in zu_notify_funcs.py')
        traceback.print_exc()
        print('Continue operation...')



if __name__ == '__main__':
    # import numpy as np
    # zu_notify(dt.datetime.now(), np.ones((25, 25, 3), dtype='uint8')*100, const.USER)

    # zu_weather()

    # zu_traffic('down')

    zu_holiday()
