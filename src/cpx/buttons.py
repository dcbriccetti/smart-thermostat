from time import monotonic, sleep
from board import BUTTON_A, BUTTON_B, A5, A6
from digitalio import DigitalInOut, Pull


class Buttons:
    'A general-purpose button press detection class. Calls the listeners with a 0 or a 1 when a button is pushed.'

    def __init__(self, button_repeat_delay_secs):
        self.button_repeat_delay_secs = button_repeat_delay_secs
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
                    self.next_button_check = time_now + self.button_repeat_delay_secs
                    self._notify_listeners(index)

    def _notify_listeners(self, index):
        for listener in self.listeners:
            listener(index)
