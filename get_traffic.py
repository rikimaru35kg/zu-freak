import traceback

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


def get_traffic(direction='down'):
    result = ''
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
            if ( (direction == 'up') and
                 (e.text.startswith('東名<上り>'))):
                if '渋滞の情報はありません' not in e.text:
                    result = e.text.replace('東名<上り>\n', '').replace('渋滞\n', '')
                break
            elif ( (direction == 'down') and
                   (e.text.startswith('東名<下り>'))):
                if '渋滞の情報はありません' not in e.text:
                    result = e.text.replace('東名<下り>\n', '').replace('渋滞\n', '')
                break
        
        driver.quit()

        return result
    except:
        traceback.print_exc()
        driver.quit()

        return result


if __name__ == '__main__':
    jam = get_traffic('up')
    if jam == '':
        print('上り渋滞なし！')
    else:
        print(jam)

    jam = get_traffic('down')
    if jam == '':
        print('下り渋滞なし！')
    else:
        print(jam)
