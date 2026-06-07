"""
服务
"""

from .base import BasePage, W, H, M, USABLE
import subprocess
import config


class ServicesPage(BasePage):
    def __init__(self):
        super().__init__()

    def _active(self, name):
        try:
            r = subprocess.run(['systemctl', 'is-active', name],
                               capture_output=True, text=True, timeout=2)
            return r.stdout.strip() == 'active'
        except Exception:
            return False

    def render(self):
        # Label
        self.text_center(24, "服务", font='small', color=config.GRAY)

        svcs = config.MONITORED_SERVICES
        n = len(svcs)
        row_h = 34
        total = n * row_h
        y0 = 24 + (H - 24 - total) // 2  # center vertically

        for i, svc in enumerate(svcs):
            y = y0 + i * row_h
            on = self._active(svc)
            c = config.WHITE if on else config.DIM

            # Dot
            self.dot(M + 4, y + 8, config.GREEN if on else config.DIM, 4)

            # Name
            self.text(M + 18, y + 2, svc, font='body', color=c)

            # Status
            self.text_right(W - M, y + 2, "ON" if on else "OFF",
                            font='body', color=config.GREEN if on else config.DIM)

        return self._image

    def get_image(self):
        self.new_canvas()
        self.render()
        return self._image
