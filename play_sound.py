import glob
import random

from playsound import playsound


def play_sound(dir):
    playsound(random.choice(glob.glob(f'{dir}/*mp3')))


if __name__ == '__main__':
    import time

    for i in range(50):
        play_sound('./audio')
        time.sleep(1)
