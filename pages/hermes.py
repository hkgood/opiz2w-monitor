"""
Hermes
"""

from .base import BasePage, W, H, M, USABLE
import config


class HermesPage(BasePage):
    def __init__(self, hermes_stats):
        super().__init__()
        self.hermes = hermes_stats

    def render(self):
        s = self.hermes.get_all_stats()
        mem = s['memory_mb']
        cpu = s['cpu_percent']

        # Label
        self.text_center(24, "HERMES", font='small', color=config.GRAY)

        # Status
        if s['running']:
            self.dot(M + 4, 52, config.GREEN, 4)
            self.text(M + 16, 48, "运行中", font='body', color=config.GREEN)
        else:
            self.dot(M + 4, 52, config.RED, 4)
            self.text(M + 16, 48, "已停止", font='body', color=config.RED)

        # Big number
        self.text_center(72, f"{mem:.0f}", font='hero')

        # Unit
        self.text_center(130, "MB", font='small', color=config.GRAY)

        # Bar
        self.bar(M, 148, USABLE, 4, min(100, mem / 40))

        # Row: cpu | pid
        self.text(M, 168, f"CPU {cpu:.1f}%", font='body', color=config.GRAY)
        self.text_right(W - M, 168, f"PID {s['pid'] or '-'}", font='body', color=config.GRAY)

        # Row: gateway
        gw = s['gateway_running']
        gc = config.GREEN if gw else config.DIM
        self.dot(M + 4, 198, gc, 3)
        self.text(M + 14, 194, f"Gateway {'在线' if gw else '离线'}", font='body', color=gc)

        return self._image

    def get_image(self):
        self.new_canvas()
        self.render()
        return self._image
