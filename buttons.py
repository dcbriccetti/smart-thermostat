from time import monotonic, sleep
from board import BUTTON_A, BUTTON_B, A5, A6
from digitalio import DigitalInOut, Pull

BUTTON_REPEAT_DELAY_SECS = 0.3


class Buttons:
    def __init__(self):
        self.next_button_check = monotonic()
        self.buttons = [DigitalInOut(pin) for pin in (BUTTON_A, BUTTON_B)]
        for button in self.buttons:
            button.switch_to_input(pull=Pull.DOWN)
        self.listeners = []

    def add_push_listener(self, l):
        self.listeners.append(l)

    def update(self):
        time_now = monotonic()
        if time_now >= self.next_button_check:
            for index, button in enumerate(self.buttons):
                if button.value:
                    self.next_button_check = time_now + BUTTON_REPEAT_DELAY_SECS
                    self._notify_listeners(index)

    def _notify_listeners(self, index):
        for listener in self.listeners:
            listener(index)
