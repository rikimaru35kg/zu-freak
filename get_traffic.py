import traceback

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


def get_traffic():
    try:
        path = '/usr/bin/chromedriver'
        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Chrome(service=Service(path), options=options)
        driver.implicitly_wait(30)
        driver.get('https://www.atis.co.jp/traffic/highway/highway/1031008/')

        elem = ( driver.find_element(By.CLASS_NAME, 'traffic-info-tabs')
                       .find_element(By.CLASS_NAME, 'tab03') )
        elem.click()

        elems = driver.find_elements(By.CLASS_NAME, 'traffic-result-row')
        for e in elems:
            if e.text.startswith('東名<下り>'):
                return e.text.replace('東名<下り>\n', '').replace('渋滞\n', '')

    except:
        traceback.print_exc()

        return ''


if __name__ == '__main__':
    print(get_traffic())
