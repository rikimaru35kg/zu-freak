import requests
from bs4 import BeautifulSoup as bs


def get_weather(dest='厚木市'):
    if dest == '厚木市':
        url = 'https://tenki.jp/forecast/3/17/4620/14212/3hours.html'
    
    res = requests.get(url)
    soup = bs(res.text, 'html.parser')
    today = soup.select_one('#forecast-point-3h-today')
    hours = [f'{v.text}時' for v in today.select_one('.hour').find_all('td')]
    weathers = [v.text.replace('\n', '')
                for v in today.select_one('.weather').find_all('td')]
    temps = [f'{v.text}[℃]' for v in today.select_one('.temperature').find_all('td')]
    probs = [f'{v.text}[%]'
             for v in today.select_one('.prob-precip').find_all('td')]
    precipitations = [f'{v.text}[mm/h]'
                      for v in today.select_one('.precipitation').find_all('td')]
    
    txt = ''
    for i in range(len(hours)):
        txt += f'{hours[i]}: {weathers[i]} {temps[i]} {probs[i]} {precipitations[i]}'
        if i != len(hours) - 1:
            txt += '\n'

    return txt


if __name__ == '__main__':
    print(get_weather('厚木市'))
