import time


class DtDetector:
    def __init__(self):
        self.reset_time()
    
    def get_dt(self):
        t_now = time.perf_counter()
        self.dt = t_now - self.t_save
        self.t_save = t_now

        return self.dt
    
    def reset_time(self):
        self.t_save = time.perf_counter()


if __name__ == '__main__':
    dt_detector = DtDetector()

    n = 0
    while n < 10:
        print(dt_detector.get_dt())
        n += 1
    time.sleep(3)
    dt_detector.reset_time()
    while n < 20:
        print(dt_detector.get_dt())
        n += 1
