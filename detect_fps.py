import time

class FpsDetector:
    def __init__(self, default_fps=25, alpha=0.1):
        self.t_save = time.perf_counter()
        self.fps = default_fps
        self.alpha = alpha
    
    def update_fps(self):
        self.fps = (self.alpha * 1 / (time.perf_counter() - self.t_save)
                    + (1 - self.alpha) * self.fps)
        self.t_save = time.perf_counter()

    def get_fps(self):
        return int(self.fps)
