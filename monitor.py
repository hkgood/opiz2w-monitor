#!/usr/bin/env python3
"""
Orange Pi Zero 2W LCD Monitor
Minimalist design inspired by Apple & Dieter Rams
"""

import sys
import os
import time
import signal
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from drivers.lcd import LCD
from drivers.buttons import ButtonHandler, ButtonEvent
from utils.metrics import SystemMetrics
from utils.hermes_stats import HermesStats
from pages.clock import ClockPage
from pages.system import SystemPage
from pages.hermes import HermesPage
from pages.network import NetworkPage
from pages.services import ServicesPage


class MonitorApp:
    def __init__(self):
        self.lcd = None
        self.buttons = None
        self.metrics = SystemMetrics()
        self.hermes = HermesStats()

        self.pages = []
        self.current_page_index = 0

        self.is_sleeping = False
        self.last_activity_time = time.time()
        self.running = False

        self._setup_signal_handlers()
        self._init_pages()

    def _setup_signal_handlers(self):
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        self.running = False

    def _init_pages(self):
        self.pages = [
            ClockPage(self.metrics),
            SystemPage(self.metrics),
            HermesPage(self.hermes),
            NetworkPage(self.metrics),
            ServicesPage(),
        ]

    def _button_callback(self, event):
        self.last_activity_time = time.time()

        if self.is_sleeping:
            self._wake_up()
            return

        if event in (ButtonEvent.UP, ButtonEvent.KEY1, ButtonEvent.LEFT):
            self._prev_page()
        elif event in (ButtonEvent.DOWN, ButtonEvent.KEY2, ButtonEvent.RIGHT):
            self._next_page()
        elif event in (ButtonEvent.KEY3, ButtonEvent.PRESS):
            self._enter_sleep()

    def _next_page(self):
        self.current_page_index = (self.current_page_index + 1) % len(self.pages)

    def _prev_page(self):
        self.current_page_index = (self.current_page_index - 1) % len(self.pages)

    def _enter_sleep(self):
        self.is_sleeping = True
        self.lcd.sleep()

    def _wake_up(self):
        self.is_sleeping = False
        self.lcd.wake()
        self.current_page_index = 0

    def _check_auto_sleep(self):
        if not self.is_sleeping:
            elapsed = time.time() - self.last_activity_time
            if elapsed >= config.SLEEP_TIMEOUT:
                self._enter_sleep()

    def run(self):
        try:
            self.lcd = LCD()
            self.buttons = ButtonHandler(callback=self._button_callback)
            self.buttons.start()
            self.running = True

            last_image = None
            while self.running:
                self._check_auto_sleep()

                if not self.is_sleeping:
                    page = self.pages[self.current_page_index]
                    image = page.get_image()
                    if image is not last_image:
                        self.lcd.display(image)
                        last_image = image
                else:
                    last_image = None

                time.sleep(0.5)

        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.cleanup()

    def cleanup(self):
        self.running = False
        if self.buttons:
            self.buttons.stop()
        if self.lcd:
            try:
                self.lcd.wake()
                self.lcd.clear()
            except Exception:
                pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sim', action='store_true')
    args = parser.parse_args()

    if args.sim:
        print("Simulation mode - no hardware")
        return

    app = MonitorApp()
    app.run()


if __name__ == '__main__':
    main()
