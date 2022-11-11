import requests

import keyring


def main():
    send_line('送りたい文章')

def send_line(notification_message, img=None, user=None):
    """Notify LINE

    Arguments:
        notification_message (str): Message to be sent
    """
    if user == 'me':
        line_notify_token = keyring.get_password('line', 'me')
    elif user == 'family':
        line_notify_token = keyring.get_password('line', 'family')
    else:
        line_notify_token = keyring.get_password('line', 'me')

    line_notify_api = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': f'Bearer {line_notify_token}'}
    data = {'message': f'{notification_message}'}

    if img is not None:
        f = open(img, 'rb')
        files = {'imageFile': f}
        requests.post(line_notify_api, headers=headers, data=data, files=files)
        f.close()
    else:
        requests.post(line_notify_api, headers=headers, data=data)

if __name__ == "__main__":
    main()

