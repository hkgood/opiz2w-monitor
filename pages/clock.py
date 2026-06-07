"""
时钟
"""

import time
from .base import BasePage, W, H, M, USABLE
import config


class ClockPage(BasePage):
    def __init__(self, metrics):
        super().__init__()
        self.metrics = metrics
        self._last_sec = -1

    def render(self):
        now = time.localtime()
        if now.tm_sec == self._last_sec:
            return self._image
        self._last_sec = now.tm_sec

        # Time - centered at y=80
        t = time.strftime("%H:%M", now)
        self.text_center(56, t, font='hero')

        # Seconds - to the right
        s = time.strftime("%S", now)
        bbox = self._draw.textbbox((0, 0), t, font=self.F['hero'])
        sx = (W - (bbox[2] - bbox[0])) // 2 + (bbox[2] - bbox[0]) + 4
        self.text(sx, 68, s, font='title', color=config.GRAY)

        # Date
        d = time.strftime("%Y年%m月%d日", now)
        self.text_center(120, d, font='body', color=config.GRAY)

        # Weekday
        wd = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][now.tm_wday]
        self.text_center(142, wd, font='small', color=config.DIM)

        # Separator
        self.line(168)

        # Bottom row
        self.text(M, 180, self.metrics.get_ip_address(), font='small', color=config.DIM)
        self.text_right(W - M, 180, self._uptime(), font='small', color=config.DIM)

        return self._image

    def _uptime(self):
        try:
            import psutil
            s = time.time() - psutil.boot_time()
            d, h, m = int(s // 86400), int(s % 86400 // 3600), int(s % 3600 // 60)
            return f"{d}天{h}时" if d else f"{h}时{m}分"
        except Exception:
            return ""

    def get_image(self):
        now = time.localtime()
        if now.tm_sec == self._last_sec and self._image is not None:
            return self._image
        self.new_canvas()
        self.render()
        return self._image
