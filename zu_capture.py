import sys
import time
import datetime

import cv2
import numpy as np
import keyring

import line_notify
import const as myv
import get_weather as gw
import get_traffic as gt
# import detect_fps as dfps


def increment_frame_num(i, max):
    """Increment frame number"""
    if (i + 1) >= max:
        return 0
    else:
        return i + 1


def zu_notify(t_now, frame, user):
    """Send LINE message
    
    Args:
        t_now (datetime): current time
        frame (np.ndarray): Image to be sent
    """
    message = \
f"""{t_now.strftime("%Y/%m/%d %H:%M:%S")}
ズーカメラで動きが検知されました。

現在のズー
{keyring.get_password('zu', 'zu1')}

現在＋過去のズー
{keyring.get_password('zu', 'zu2')}"""

    cv2.imwrite('zu.png', frame)
    line_notify.send_line(message, 'zu.png', user)
    cv2.imwrite(f'videos/pictures/debug_{t_now.strftime("%y%m%d_%H%M%S")}.png', roi)


cap = cv2.VideoCapture('http://192.168.10.99:8080/?action=stream')
# cap = cv2.VideoCapture('./videos/test_samples/zu_record_20221028_065015.mp4')
# cap = cv2.VideoCapture('./videos/test_samples/zu_record_20221028_073516.mp4')
# cap = cv2.VideoCapture('./videos/test_samples/zu_record_20221028_074016.mp4')
# cap = cv2.VideoCapture('./videos/test_samples/zu_record_20221028_085016.mp4')
# cap = cv2.VideoCapture('./videos/test_samples/zu_record_20221104_084702.mp4')

# Preparation
roi_size = (myv.ROI[2]-myv.ROI[0], myv.ROI[3]-myv.ROI[1])
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
v_move = 0

# fps = dfps.FpsDetector()

# Main procedure
frame_num = 0
frame_cycle = myv.FRAME_CYCLE
while True:
    ###############################
    # Stop procdure from TIME_STOP ~ TIME_START
    ###############################
    t_now = datetime.datetime.now()
    if t_now.hour >= myv.TIME_STOP:
        message = \
f"""{t_now.strftime("%Y/%m/%d %H:%M:%S")}
今日も一日お疲れ様でした。
ズーカメラは明日の朝{myv.TIME_START}時までお休みします。"""
        line_notify.send_line(message, user=myv.USER, stamp=True)

        # sleep until TIME_START
        time_start = datetime.datetime(t_now.year, t_now.month, t_now.day,
                                       myv.TIME_START, t_now.minute, t_now.second)
        t_delta = time_start + datetime.timedelta(days=1) - t_now
        time.sleep(t_delta.seconds)

        # Recalculate t_now
        t_now = datetime.datetime.now()

        # Get weather
        txt = f'おはようございます\n今日の厚木市の天気だワン\n{gw.get_weather("厚木市")}'
        line_notify.send_line(txt, user=myv.USER)

        # Get traffic
        jam = gt.get_traffic()
        if jam == '':
            txt = f'\n今は東名下りに渋滞は無いみたいだワン'
        else:
            txt = f'\n東名下りに渋滞が発生しているワン\n{jam}'
        line_notify.send_line(txt, user=myv.USER, stamp=True)

    ###############################
    # get video frame (only one time per FRAME_CYCLE)
    ###############################
    if frame_num == 0:
        ret, frame = cap.read()
        frame_num = increment_frame_num(frame_num, frame_cycle)
        # fps.update_fps()
        # print(fps.get_fps())
        
        # Read error
        if not ret:
            time.sleep(0.02)
            continue
    else:
        # Read capture, but not doing anything (skipping)
        cap.read()
        frame_num = increment_frame_num(frame_num, frame_cycle)
        continue

    ###############################
    # ROI
    ###############################
    roi = frame[myv.ROI[1]:myv.ROI[3], myv.ROI[0]:myv.ROI[2], :].copy()

    ###############################
    # gray scale
    ###############################
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    ###############################
    # two different moving averages
    ###############################
    if 'avg_long' not in locals():
        avg_long = gray.copy().astype('float')
    else:
        cv2.accumulateWeighted(gray, avg_long, myv.FILT_GRAY_LONG)

    if 'avg_short' not in locals():
        avg_short = gray.copy().astype('float')
    else:
        cv2.accumulateWeighted(gray, avg_short, myv.FILT_GRAY_SHORT)

    diff = cv2.absdiff(cv2.convertScaleAbs(avg_short), cv2.convertScaleAbs(avg_long))

    ###############################
    # binalize & close/open
    ###############################
    binalized = cv2.threshold(diff, myv.THRE_BIN_LOW, 255, cv2.THRESH_BINARY)[1]

    closed = cv2.morphologyEx(binalized, cv2.MORPH_CLOSE, kernel, iterations=myv.N_CLOSE)
    opened = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel, iterations=myv.N_OPEN)
 
    ###############################
    # contours
    ###############################
    contours, hierarchy = cv2.findContours(opened.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    infoframe = roi.copy()
    cv2.drawContours(infoframe, contours, -1, (0, 255, 0), 1)
    cont_rects = [cv2.boundingRect(c) for c in contours]
    for rect in cont_rects:
        if rect[2] >= myv.THRE_WIDTH and rect[3] >= myv.THRE_HEIGHT:
            pt1 = (rect[0], rect[1])
            pt2 = (rect[0] + rect[2], rect[1]+rect[3])
            cv2.rectangle(infoframe, pt1, pt2, (255, 0, 0), 1)

    ###############################
    # move value (possibility 0~100)
    ###############################
    # Count the number of objects detected
    cnt_obj = 0
    for rect in cont_rects:
        if rect[2] >= myv.THRE_WIDTH and rect[3] >= myv.THRE_HEIGHT:
            cnt_obj = min(cnt_obj + 1, len(myv.V_MOVE_INC) - 1)

    # Increment t_move
    if cnt_obj > 0:
        v_move = min(v_move + myv.V_MOVE_INC[cnt_obj - 1], myv.V_MOVE_MAX)
    # Decrement t_move
    else:
        v_move = max(v_move - myv.V_MOVE_DEC, 0)
    
    cv2.putText(infoframe, f'v_move={v_move:.1f}', (10, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)

    ###############################
    # LINE Notification
    ###############################
    if v_move >= myv.V_MOVE_THRE:
        # First detection
        if 't_save' not in locals():
            # t_now = datetime.datetime.now()
            zu_notify(t_now, roi, myv.USER)
            t_save = t_now
        # After first detection
        else:
            # t_now = datetime.datetime.now()
            if (t_now - t_save).seconds >= myv.INTERVAL:
                zu_notify(t_now, roi, myv.USER)
                t_save = t_now
        
    ###############################
    # show video frame
    ###############################
    if '--nodisplay' not in sys.argv[1:]:
        hybrid = np.ndarray((roi_size[1]*myv.DISP_SIZE[1], roi_size[0]*myv.DISP_SIZE[0], 3), dtype='uint8')
        hybrid[0*roi_size[1]:1*roi_size[1], 0*roi_size[0]:1*roi_size[0]] = roi
        hybrid[0*roi_size[1]:1*roi_size[1], 1*roi_size[0]:2*roi_size[0]] = cv2.cvtColor(cv2.convertScaleAbs(avg_long), cv2.COLOR_GRAY2BGR)
        hybrid[0*roi_size[1]:1*roi_size[1], 2*roi_size[0]:3*roi_size[0]] = cv2.cvtColor(cv2.convertScaleAbs(avg_short), cv2.COLOR_GRAY2BGR)
        hybrid[1*roi_size[1]:2*roi_size[1], 0*roi_size[0]:1*roi_size[0]] = cv2.cvtColor(diff, cv2.COLOR_GRAY2BGR)
        hybrid[1*roi_size[1]:2*roi_size[1], 1*roi_size[0]:2*roi_size[0]] = cv2.cvtColor(binalized, cv2.COLOR_GRAY2BGR)
        hybrid[1*roi_size[1]:2*roi_size[1], 2*roi_size[0]:3*roi_size[0]] = cv2.cvtColor(closed, cv2.COLOR_GRAY2BGR)
        hybrid[2*roi_size[1]:3*roi_size[1], 0*roi_size[0]:1*roi_size[0]] = cv2.cvtColor(opened, cv2.COLOR_GRAY2BGR)
        hybrid[2*roi_size[1]:3*roi_size[1], 1*roi_size[0]:2*roi_size[0]] = infoframe
        hybrid[2*roi_size[1]:3*roi_size[1], 2*roi_size[0]:3*roi_size[0]] = 0
    
        cv2.imshow('hy', hybrid)

    # ###############################
    # # Update frame cycle
    # ###############################
    # if ( (frame_cycle == myv.FRAME_CYCLE) and
    #      (fps.get_fps() <= 13)):
    #     frame_cycle = 1
    #     print(f'frame_cycle is changed to {frame_cycle}')
    # elif ( (frame_cycle < myv.FRAME_CYCLE) and
    #        (fps.get_fps() >= 20)):
    #     frame_cycle = myv.FRAME_CYCLE
    #     print(f'frame_cycle is changed to {frame_cycle}')

    ###############################
    # wait key
    ###############################
    input_key = cv2.waitKey(1)
    if input_key in [27, ord('q')]:
        break

cap.release()
cv2.destroyAllWindows()
