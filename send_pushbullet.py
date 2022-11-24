import keyring
from pushbullet import PushBullet

def send_pushbullet(title='', message=''):
    pb = PushBullet(keyring.get_password('pushbullet', 'me'))
    pb.push_note(title, message)

if __name__ == '__main__':
    send_pushbullet('タイトル', 'メッセージ')
