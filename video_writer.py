import os
import glob
import datetime as dt
from stat import FILE_ATTRIBUTE_ARCHIVE

import cv2
import numpy as np

import detect_fps

# CONSTANTS
VIDEO_LENGTH_SEC = 300
NUM_VIDEOS = int(12*60*60/VIDEO_LENGTH_SEC)
RESOLUTION = (640, 360)
FILENAME_HEAD = 'zu_record'
VIDEO_FOLDER = './videos'

# Capture USB camera & set configurations
cap = cv2.VideoCapture('http://192.168.10.99:8080/?action=stream')
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)
fourcc_int = int(cap.get(cv2.CAP_PROP_FOURCC))
fourcc = list((fourcc_int.to_bytes(4, 'little').decode('utf-8')))
# cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
# cap.set(cv2.CAP_PROP_EXPOSURE, 3000)

# Print USB camera information
print('width: ', cap.get(cv2.CAP_PROP_FRAME_WIDTH))
print('height: ', cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print('fps: ', cap.get(cv2.CAP_PROP_FPS))
print('fourcc: ', fourcc)
# print('exposure: ', cap.get(cv2.CAP_PROP_AUTO_EXPOSURE))
# print('buffer size: ', cap.get(cv2.CAP_PROP_BUFFERSIZE))
print('')

# Set videowriter
fourcc = cv2.VideoWriter_fourcc(*'avc1')
# initial video file name
dt_save = dt.datetime.now()
filename = f'{FILENAME_HEAD}_{dt_save.strftime("%Y%m%d_%H%M%S")}.mp4'
filepath = os.path.join(f'{VIDEO_FOLDER}', filename)
os.makedirs(VIDEO_FOLDER, exist_ok=True)
video = cv2.VideoWriter(filepath, fourcc, fps, RESOLUTION)
print('Recording videos...')

# Detect fps object instance
fps_detector = detect_fps.FpsDetector(default_fps=fps, alpha=0.1)

try:
    while True:
        # estimate fps
        fps_detector.update_fps()

        # get video frame
        ret, frame_org = cap.read()
        frame = cv2.resize(frame_org, RESOLUTION)

        # write video
        if (dt.datetime.now() - dt_save).seconds >= VIDEO_LENGTH_SEC:
            # change video file name
            dt_save = dt.datetime.now()
            filename = f'{FILENAME_HEAD}_{dt_save.strftime("%Y%m%d_%H%M%S")}.mp4'
            filepath = os.path.join(f'{VIDEO_FOLDER}', filename)
            fps = fps_detector.get_fps()
            video = cv2.VideoWriter(filepath, fourcc, fps, RESOLUTION)

            # delete old videos
            search_criteria = os.path.join(f'{VIDEO_FOLDER}', f'{FILENAME_HEAD}*')
            filepaths = sorted(glob.glob(search_criteria))
            for f in filepaths[:-NUM_VIDEOS]:
                os.remove(f)

        video.write(frame)

except KeyboardInterrupt as e:
    print('\nKeyboardInterrupt detected')
    cap.release()
