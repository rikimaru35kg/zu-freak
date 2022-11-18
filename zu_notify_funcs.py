import time
import datetime as dt

import requests

import const
import line_notify
import get_weather
import get_traffic


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
    txt = f'\nおはようございます\n今日の厚木市の天気だワン\n{get_weather.get_weather("厚木市")}'
    line_notify.send_line(txt, user=const.USER)


def zu_traffic():
    jam = get_traffic.get_traffic()
    if jam == '':
        txt = f'\n今は東名下りに渋滞は無いみたいだワン'
    else:
        txt = f'\n東名下りに渋滞が発生しているワン\n{jam}'
    line_notify.send_line(txt, user=const.USER, stamp=True)


def zu_holiday():
    """Send holiday information by LINE"""
    now = dt.datetime.now()
    year = now.year
    cw_this = now.isocalendar().week
    cw_next = (now + dt.timedelta(weeks=1)).isocalendar().week

    holidays = []
    for y in [year, year + 1]:
        url = 'https://api.national-holidays.jp/' + str(y)
        res = requests.get(url)
        holidays += res.json()

    h_thisweek = []
    for holiday in holidays:
        _year = dt.datetime.strptime(holiday['date'], '%Y-%m-%d').year
        _cw = dt.datetime.strptime(holiday['date'], '%Y-%m-%d').isocalendar().week
        if ( ( (_year == year) and
               (_cw == cw_this)) or
             ( (_year == year + 1) and
               (_cw == cw_next))):
            h_thisweek.append(holiday)

    if len(h_thisweek) > 0:
        message = '今週と来週の祝日情報だワン'
        for d in h_thisweek:
            message += f'\n{d["date"]}: {d["name"]}({d["type"]})'
        
        line_notify.send_line(message, user=const.USER, stamp=True)



if __name__ == '__main__':
    zu_sleep()
