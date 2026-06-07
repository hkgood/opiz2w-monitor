"""
Orange Pi Zero 2W LCD Monitor
Design: Apple / Dieter Rams minimalist
"""

# Display
DISPLAY_WIDTH = 240
DISPLAY_HEIGHT = 240

# SPI
SPI_PORT = 1
SPI_CS = 0
SPI_FREQ = 20000000

# GPIO
GPIO_DC = "PI6"
GPIO_RST = "PI14"
GPIO_BL = "PI7"

# Buttons
GPIO_KEY1 = "PI3"
GPIO_KEY2 = "PI5"
GPIO_KEY3 = "PI4"
GPIO_JOY_UP = "PI0"
GPIO_JOY_DOWN = "PI1"
GPIO_JOY_LEFT = "PI2"
GPIO_JOY_RIGHT = "PI9"
GPIO_JOY_PRESS = "PI8"

# Timing
BUTTON_DEBOUNCE_MS = 50
SLEEP_TIMEOUT = 30
REFRESH_RATE = 0.5

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (140, 140, 140)
DIM = (70, 70, 70)
DARK = (30, 30, 30)
ACCENT = (100, 180, 255)
GREEN = (80, 200, 120)
RED = (240, 80, 80)

# Grid - consistent spacing
PX = 4  # base unit
MARGIN = 24
GAP = 12

# Services
MONITORED_SERVICES = [
    'hermes-gateway',
    'ssh',
    'nginx',
    'docker',
    'bluetooth',
]

HERMES_PROCESS_NAME = 'hermes'
HERMES_INSTALL_DIR = '/root/.hermes/hermes-agent'

# Fonts
FONT_DIR = '/usr/share/fonts/'
FONT_CN = FONT_DIR + 'truetype/wqy/wqy-zenhei.ttc'
FONT_EN = FONT_DIR + 'truetype/dejavu/DejaVuSans.ttf'
FONT_EN_BOLD = FONT_DIR + 'truetype/dejavu/DejaVuSans-Bold.ttf'
