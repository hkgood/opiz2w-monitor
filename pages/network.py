"""
网络
"""

from .base import BasePage, W, H, M, USABLE
import config


class NetworkPage(BasePage):
    def __init__(self, metrics):
        super().__init__()
        self.metrics = metrics

    def render(self):
        wifi = self.metrics.get_wifi_info()
        ip = self.metrics.get_ip_address()
        speed = self.metrics.get_network_speed()

        # Label
        self.text_center(24, "网络", font='small', color=config.GRAY)

        # IP
        self.text_center(60, ip, font='title')

        # Status
        if wifi['connected']:
            self.dot(M + 56, 94, config.GREEN, 4)
            self.text(M + 68, 90, "已连接", font='body', color=config.GREEN)
        else:
            self.dot(M + 56, 94, config.RED, 4)
            self.text(M + 68, 90, "未连接", font='body', color=config.RED)

        # SSID
        ssid = wifi.get('ssid', '')
        if ssid:
            self.text_center(118, ssid, font='body', color=config.GRAY)

        # Separator
        self.line(144)

        # Upload
        up = speed['upload_kb']
        self.text(M, 156, "↑", font='body', color=config.GREEN)
        up_s = f"{up/1024:.1f}M/s" if up > 1024 else f"{up:.0f}K/s"
        self.text(M + 20, 156, up_s, font='body')

        # Download
        dn = speed['download_kb']
        self.text(M, 182, "↓", font='body', color=config.ACCENT)
        dn_s = f"{dn/1024:.1f}M/s" if dn > 1024 else f"{dn:.0f}K/s"
        self.text(M + 20, 182, dn_s, font='body')

        # Signal
        if wifi['connected']:
            sig = wifi['signal_dbm']
            q = min(100, max(0, (sig + 100) * 2))
            self.text(M, 208, f"信号 {sig}dBm", font='small', color=config.DIM)
            self.bar(W - M - 60, 210, 60, 3, q, config.WHITE)

        return self._image

    def get_image(self):
        self.new_canvas()
        self.render()
        return self._image
