"""
CPU
"""

from .base import BasePage, W, H, M, USABLE
import config
import os


class SystemPage(BasePage):
    def __init__(self, metrics):
        super().__init__()
        self.metrics = metrics

    def render(self):
        d = self.metrics.get_all_metrics()
        cpu = d['cpu_percent']
        t = d['temperature']
        l1, l5, l15 = d['load_avg']
        disk = d['disk']

        # Label
        self.text_center(24, "CPU", font='small', color=config.GRAY)

        # Big number
        c = config.WHITE if cpu < 70 else config.RED
        self.text_center(56, f"{cpu:.0f}%", font='hero', color=c)

        # Bar
        self.bar(M, 124, USABLE, 5, cpu, c)

        # Row: temp | cores
        self.text(M, 144, f"温度 {t:.0f}°", font='body', color=config.GRAY)
        cores = os.cpu_count() or 4
        self.text_right(W - M, 144, f"{cores} 核心", font='body', color=config.GRAY)

        # Row: load
        self.text(M, 172, "负载", font='small', color=config.DIM)
        self.text(M + 40, 172, f"{l1:.2f}", font='body',
                  color=config.WHITE if l1 < 1.0 else config.RED)
        self.text(M + 90, 172, f"{l5:.2f}", font='body', color=config.GRAY)
        self.text(M + 140, 172, f"{l15:.2f}", font='body', color=config.DIM)

        # Row: disk
        self.text(M, 198, "存储", font='small', color=config.DIM)
        self.bar(M + 44, 200, USABLE - 88, 4, disk['percent'],
                 config.WHITE if disk['percent'] < 85 else config.RED)
        self.text_right(W - M, 196, f"{disk['percent']:.0f}%", font='body', color=config.GRAY)

        return self._image

    def get_image(self):
        self.new_canvas()
        self.render()
        return self._image
