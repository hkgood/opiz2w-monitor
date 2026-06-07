"""
Button Handler for Waveshare 1.3inch LCD HAT
Uses OPi.GPIO with SUNXI naming for Orange Pi Zero 2W
Supports joystick (5-way) and 3 push buttons
"""

import time
import threading
from collections import deque

import OPi.GPIO as GPIO

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

GPIO.setwarnings(False)
GPIO.setmode(GPIO.SUNXI)


class ButtonEvent:
    UP = 'up'
    DOWN = 'down'
    LEFT = 'left'
    RIGHT = 'right'
    PRESS = 'press'
    KEY1 = 'key1'
    KEY2 = 'key2'
    KEY3 = 'key3'
    NONE = 'none'


class ButtonHandler:
    """Handle button input with debounce"""

    def __init__(self, callback=None):
        self.callback = callback
        self._running = False
        self._thread = None
        self._button_states = {}
        self._last_press_time = {}
        self._event_queue = deque(maxlen=10)
        self._lock = threading.Lock()
        self._use_gpio = False

        self._pin_map = {
            config.GPIO_JOY_UP: ButtonEvent.UP,
            config.GPIO_JOY_DOWN: ButtonEvent.DOWN,
            config.GPIO_JOY_LEFT: ButtonEvent.LEFT,
            config.GPIO_JOY_RIGHT: ButtonEvent.RIGHT,
            config.GPIO_JOY_PRESS: ButtonEvent.PRESS,
            config.GPIO_KEY1: ButtonEvent.KEY1,
            config.GPIO_KEY2: ButtonEvent.KEY2,
            config.GPIO_KEY3: ButtonEvent.KEY3,
        }

        self._init_gpio()

    def _init_gpio(self):
        """Initialize GPIO pins for buttons"""
        try:
            for pin_name in self._pin_map.keys():
                try:
                    GPIO.setup(pin_name, GPIO.IN)
                    self._button_states[pin_name] = False
                    self._last_press_time[pin_name] = 0
                except Exception:
                    continue

            self._use_gpio = len(self._button_states) > 0
        except Exception:
            self._use_gpio = False

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
        try:
            GPIO.cleanup()
        except Exception:
            pass

    def _monitor_loop(self):
        """Main button monitoring loop"""
        while self._running:
            current_time = time.time() * 1000

            for pin_name, event_name in self._pin_map.items():
                try:
                    val = GPIO.input(pin_name)
                    pressed = (val == GPIO.LOW)  # Active low (pull-up)
                    was_pressed = self._button_states.get(pin_name, False)

                    if pressed and not was_pressed:
                        last_time = self._last_press_time.get(pin_name, 0)
                        if current_time - last_time > config.BUTTON_DEBOUNCE_MS:
                            self._button_states[pin_name] = True
                            self._last_press_time[pin_name] = current_time
                            self._emit_event(event_name)

                    elif not pressed and was_pressed:
                        self._button_states[pin_name] = False

                except Exception:
                    continue

            time.sleep(0.01)

    def _emit_event(self, event_name):
        with self._lock:
            self._event_queue.append(event_name)
        if self.callback:
            self.callback(event_name)

    def get_event(self):
        with self._lock:
            if self._event_queue:
                return self._event_queue.popleft()
        return ButtonEvent.NONE

    def wait_event(self, timeout=None):
        start = time.time()
        while True:
            event = self.get_event()
            if event != ButtonEvent.NONE:
                return event
            if timeout and (time.time() - start) >= timeout:
                return ButtonEvent.NONE
            time.sleep(0.01)
