# LINE receiver
# USER = 'family'
USER = 'me'

# STOP & START time [hour]
TIME_START = 6
TIME_1 = 12
TIME_2 = 18
TIME_STOP = 21

# Input image resolution & ROI
RESOLUTION = (640, 360)
ROI = (300, 100, 580, 250)  # (X0, Y0, X1, Y1)

# 1 process / FRAME_CYCLE to reduce calculation cost
FRAME_CYCLE = 2

# Tuning parameters
# Moving average
FILT_GRAY_LONG = 0.05
FILT_GRAY_SHORT = 0.1
# Pick-up threshold (from diff image)
THRE_BIN_LOW = 10
# Close kernel size [px]
N_CLOSE = 3
# Open kernel size [px]
N_OPEN = 4
# Threshold of detected contour width [px]
THRE_WIDTH = 30
# Threshold of detected contour height [px]
THRE_HEIGHT = 30
# V_MOVE tuning parameters
V_MOVE_INC = [1.5, 1.5, 1.8]
V_MOVE_DEC = 2
V_MOVE_MAX = 100
V_MOVE_THRE = 95

# LINE notification interval
INTERVAL = 600  # [sec]

# imshow size for debugging
DISP_SIZE = (3, 3)

# LINE stamp
LINE_STAMP = {446: list(range(1998, 2028)),
              789: list(range(10855, 10895)),
              1070: list(range(17839, 17879)),
              6136: list(range(10551376, 10551400)),
              8515: list(range(16581242, 16581266)),
              11537: list(range(52002734, 52002774)),
              11538: list(range(51626494, 51626534)),
              11539: list(range(52114110, 52114150)),
              6325: list(range(10979904, 10979928))}
