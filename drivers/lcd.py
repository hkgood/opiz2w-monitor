"""
LCD Driver for Waveshare 1.3inch LCD HAT (ST7789VM, 240x240)
Uses OPi.GPIO + spidev for Orange Pi Zero 2W
"""

import time
import spidev
import OPi.GPIO as GPIO
from PIL import Image
import numpy as np

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

GPIO.setwarnings(False)
GPIO.setmode(GPIO.SUNXI)


class ST7789VMDriver:
    """ST7789VM driver for 1.3inch LCD HAT"""

    def __init__(self):
        self.width = config.DISPLAY_WIDTH
        self.height = config.DISPLAY_HEIGHT

        self._spi = spidev.SpiDev()
        self._init_gpio()
        self._init_spi()
        self._init_display()

    def _init_gpio(self):
        GPIO.setup(config.GPIO_DC, GPIO.OUT)
        GPIO.setup(config.GPIO_RST, GPIO.OUT)
        GPIO.setup(config.GPIO_BL, GPIO.OUT)
        GPIO.output(config.GPIO_BL, GPIO.HIGH)

    def _init_spi(self):
        self._spi.open(config.SPI_PORT, config.SPI_CS)
        self._spi.max_speed_hz = config.SPI_FREQ
        self._spi.mode = 0b00
        self._spi.bits_per_word = 8

    def _write_reg(self, reg):
        GPIO.output(config.GPIO_DC, GPIO.LOW)
        self._spi.writebytes([reg])

    def _write_data_8bit(self, data):
        GPIO.output(config.GPIO_DC, GPIO.HIGH)
        self._spi.writebytes([data])

    def _write_data_bulk(self, data):
        GPIO.output(config.GPIO_DC, GPIO.HIGH)
        for i in range(0, len(data), 4096):
            self._spi.writebytes(data[i:i+4096])

    def _hardware_reset(self):
        GPIO.output(config.GPIO_RST, GPIO.HIGH)
        time.sleep(0.05)
        GPIO.output(config.GPIO_RST, GPIO.LOW)
        time.sleep(0.05)
        GPIO.output(config.GPIO_RST, GPIO.HIGH)
        time.sleep(0.12)

    def _init_display(self):
        """ST7789VM initialization - Waveshare 1.3inch official sequence"""
        GPIO.output(config.GPIO_BL, GPIO.HIGH)
        self._hardware_reset()

        # Sleep out
        self._write_reg(0x11)
        time.sleep(0.12)

        # MADCTL - Memory Data Access Control (0x60 = 90° clockwise rotation)
        self._write_reg(0x36)
        self._write_data_8bit(0x60)

        # COLMOD - Interface Pixel Format (16-bit RGB565)
        self._write_reg(0x3A)
        self._write_data_8bit(0x05)

        # Porch Control
        self._write_reg(0xB2)
        self._write_data_8bit(0x0C)
        self._write_data_8bit(0x0C)
        self._write_data_8bit(0x00)
        self._write_data_8bit(0x33)
        self._write_data_8bit(0x33)

        # Gate Control
        self._write_reg(0xB7)
        self._write_data_8bit(0x35)

        # VCOM Setting
        self._write_reg(0xBB)
        self._write_data_8bit(0x19)

        # LCM Control
        self._write_reg(0xC0)
        self._write_data_8bit(0x2C)

        # VDV and VRH Command Enable
        self._write_reg(0xC2)
        self._write_data_8bit(0x01)

        # VRH Set
        self._write_reg(0xC3)
        self._write_data_8bit(0x12)

        # VDV Set
        self._write_reg(0xC4)
        self._write_data_8bit(0x20)

        # Frame Rate Control
        self._write_reg(0xC6)
        self._write_data_8bit(0x0F)

        # Power Control 1
        self._write_reg(0xD0)
        self._write_data_8bit(0xA4)
        self._write_data_8bit(0xA1)

        # GIP Map (positive voltage)
        self._write_reg(0xE0)
        for val in [0xD0, 0x08, 0x0E, 0x09, 0x09, 0x05, 0x31, 0x33,
                    0x48, 0x17, 0x14, 0x15, 0x31, 0x34]:
            self._write_data_8bit(val)

        # GIP Map (negative voltage)
        self._write_reg(0xE1)
        for val in [0xD0, 0x08, 0x0E, 0x09, 0x09, 0x15, 0x31, 0x33,
                    0x48, 0x17, 0x14, 0x15, 0x31, 0x34]:
            self._write_data_8bit(val)

        # Display Inversion On (required for ST7789)
        self._write_reg(0x21)

        # Display On
        self._write_reg(0x29)
        time.sleep(0.05)

    def _set_window(self, x0, y0, x1, y1):
        """Set display window"""
        self._write_reg(0x2A)
        self._write_data_8bit(0x00)
        self._write_data_8bit(x0)
        self._write_data_8bit(0x00)
        self._write_data_8bit(x1)

        self._write_reg(0x2B)
        self._write_data_8bit(0x00)
        self._write_data_8bit(y0)
        self._write_data_8bit(0x00)
        self._write_data_8bit(y1)

        self._write_reg(0x2C)

    def clear(self):
        """Clear display to black"""
        _buffer = [0x00] * (self.width * self.height * 2)
        self._set_window(0, 0, self.width - 1, self.height - 1)
        GPIO.output(config.GPIO_DC, GPIO.HIGH)
        for i in range(0, len(_buffer), 4096):
            self._spi.writebytes(_buffer[i:i+4096])

    def display_image(self, image):
        """Display PIL Image with RGB565 conversion"""
        if image.size != (self.width, self.height):
            image = image.resize((self.width, self.height))

        img = np.asarray(image)
        pix = np.zeros((self.width, self.height, 2), dtype=np.uint8)
        pix[..., 0] = np.add(np.bitwise_and(img[..., 0], 0xF8),
                              np.right_shift(img[..., 1], 5))
        pix[..., 1] = np.add(np.bitwise_and(np.left_shift(img[..., 1], 3), 0xE0),
                              np.right_shift(img[..., 2], 3))
        pix = pix.flatten().tolist()

        self._set_window(0, 0, self.width - 1, self.height - 1)
        GPIO.output(config.GPIO_DC, GPIO.HIGH)
        for i in range(0, len(pix), 4096):
            self._spi.writebytes(pix[i:i+4096])

    def set_backlight(self, state):
        GPIO.output(config.GPIO_BL, GPIO.HIGH if state else GPIO.LOW)

    def sleep(self):
        self._write_reg(0x10)  # Sleep in
        time.sleep(0.05)
        self.set_backlight(False)

    def wake(self):
        self.set_backlight(True)
        self._write_reg(0x11)  # Sleep out
        time.sleep(0.12)
        self._write_reg(0x29)  # Display on
        time.sleep(0.05)

    def close(self):
        self._spi.close()
        GPIO.cleanup()


class LCD:
    """LCD display driver wrapper"""

    def __init__(self):
        self.driver = ST7789VMDriver()

    def clear(self):
        self.driver.clear()

    def display(self, image):
        self.driver.display_image(image)

    def create_image(self, mode='RGB'):
        return Image.new(mode, (self.driver.width, self.driver.height), (0, 0, 0))

    def set_backlight(self, state):
        self.driver.set_backlight(state)

    def sleep(self):
        self.driver.sleep()

    def wake(self):
        self.driver.wake()

    def close(self):
        self.driver.close()
