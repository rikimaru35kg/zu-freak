import sys
import time
import datetime

import cv2
import numpy as np

import const as myv
import zu_notify_funcs as zu


def increment_frame_num(i, max):
    """Increment frame number"""
    if (i + 1) >= max:
        return 0
    else:
        return i + 1

# Capture the video
cap = cv2.VideoCapture('http://192.168.10.99:8080/?action=stream')

# Preparation
roi_size = (myv.ROI[2]-myv.ROI[0], myv.ROI[3]-myv.ROI[1])
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
v_move = 0

# Main procedure
frame_num = 0
frame_cycle = myv.FRAME_CYCLE
while True:
    ###############################
    # Stop procdure from TIME_STOP ~ TIME_START
    ###############################
    t_now = datetime.datetime.now()
    if t_now.hour >= myv.TIME_STOP:
        # Sleep until TIME_START
        zu.zu_sleep()

        # Send weather information
        zu.zu_weather()

        # Send traffic information
        zu.zu_traffic()

        # Recalculate t_now
        t_now = datetime.datetime.now()

        # Send holiday information
        if t_now.isoweekday() == 1:
            zu.zu_holiday()

    ###############################
    # get video frame (only one time per FRAME_CYCLE)
    ###############################
    if frame_num == 0:
        ret, frame = cap.read()
        frame_num = increment_frame_num(frame_num, frame_cycle)
        
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
            zu.zu_notify(t_now, roi, myv.USER)
            t_save = t_now
        # After first detection
        else:
            if (t_now - t_save).seconds >= myv.INTERVAL:
                zu.zu_notify(t_now, roi, myv.USER)
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

    ###############################
    # wait key
    ###############################
    input_key = cv2.waitKey(1)
    if input_key in [27, ord('q')]:
        break

cap.release()
cv2.destroyAllWindows()
