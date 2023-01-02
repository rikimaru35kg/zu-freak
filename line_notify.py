import requests
import random
import traceback
import datetime

import keyring

import const


def main():
    send_line('送りたい文章', user='me', stamp=True)

def send_line(notification_message, img=None, user=None, stamp=False):
    """Notify LINE

    Arguments:
        notification_message (str): Message to be sent
        img (str): Image file path
        user (str): LINE user
        stamp (bool): Send stamp or not
    """
    try:
        if user == 'me':
            line_notify_token = keyring.get_password('line', 'me')
        elif user == 'family':
            line_notify_token = keyring.get_password('line', 'family')
        else:
            line_notify_token = keyring.get_password('line', 'me')

        line_notify_api = 'https://notify-api.line.me/api/notify'
        headers = {'Authorization': f'Bearer {line_notify_token}'}
        if stamp:
            package = random.choice(list(const.LINE_STAMP.keys()))
            sticker = random.choice(const.LINE_STAMP[package])
            data = {'message': f'{notification_message}', 'stickerPackageId': package, 'stickerId': sticker}
        else:
            data = {'message': f'{notification_message}'}

        if img is not None:
            f = open(img, 'rb')
            files = {'imageFile': f}
            requests.post(line_notify_api, headers=headers, data=data, files=files)
            f.close()
        else:
            requests.post(line_notify_api, headers=headers, data=data)
    except:
        print('-------------------------------------------')
        print(f'Error: {datetime.datetime.now().strftime("%Y/%m/%d-%H:%M:%S")}')
        print('Location: send_line() in line_notify.py')
        traceback.print_exc()
        print('Continue operation...')


if __name__ == "__main__":
    main()

