"""
Base page - Precise grid system
Apple / Dieter Rams aesthetic
"""

from PIL import Image, ImageDraw, ImageFont

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

W = config.DISPLAY_WIDTH
H = config.DISPLAY_HEIGHT
M = config.MARGIN
USABLE = W - 2 * M  # 192px


class BasePage:
    _fonts = {}

    def __init__(self):
        self._image = None
        self._draw = None
        self._init_fonts()

    def _init_fonts(self):
        if not BasePage._fonts:
            try:
                BasePage._fonts = {
                    'hero': ImageFont.truetype(config.FONT_EN_BOLD, 52),
                    'title': ImageFont.truetype(config.FONT_EN_BOLD, 18),
                    'body': ImageFont.truetype(config.FONT_CN, 14),
                    'small': ImageFont.truetype(config.FONT_CN, 11),
                }
            except Exception:
                f = ImageFont.load_default()
                BasePage._fonts = {k: f for k in ['hero', 'title', 'body', 'small']}

    @property
    def F(self):
        return BasePage._fonts

    def new_canvas(self):
        self._image = Image.new('RGB', (W, H), config.BLACK)
        self._draw = ImageDraw.Draw(self._image)
        return self._image

    # --- Drawing primitives ---

    def text(self, x, y, s, font='body', color=config.WHITE):
        self._draw.text((x, y), s, fill=color, font=self.F[font])

    def text_center(self, y, s, font='body', color=config.WHITE):
        bbox = self._draw.textbbox((0, 0), s, font=self.F[font])
        tw = bbox[2] - bbox[0]
        self._draw.text(((W - tw) // 2, y), s, fill=color, font=self.F[font])

    def text_right(self, x, y, s, font='body', color=config.WHITE):
        bbox = self._draw.textbbox((0, 0), s, font=self.F[font])
        tw = bbox[2] - bbox[0]
        self._draw.text((x - tw, y), s, fill=color, font=self.F[font])

    def bar(self, x, y, w, h, pct, color=config.WHITE):
        self._draw.rounded_rectangle([(x, y), (x + w, y + h)], radius=h // 2, fill=config.DARK)
        fw = max(0, int(w * min(pct, 100) / 100))
        if fw > h:
            self._draw.rounded_rectangle([(x, y), (x + fw, y + h)], radius=h // 2, fill=color)

    def dot(self, x, y, color, r=3):
        self._draw.ellipse([(x, y), (x + r * 2, y + r * 2)], fill=color)

    def line(self, y):
        self._draw.line([(M, y), (W - M, y)], fill=config.DIM, width=1)

    def render(self):
        raise NotImplementedError

    def get_image(self):
        self.new_canvas()
        self.render()
        return self._image
