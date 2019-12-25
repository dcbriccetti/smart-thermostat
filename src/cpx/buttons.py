from time import monotonic
from board import BUTTON_A, BUTTON_B
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

    def on_change(self, listener):
        self.listeners.append(listener)

    def update(self):
        time_now = monotonic()
        if time_now >= self.next_button_check:
            for index, button in enumerate(self.buttons):
                if button.value:
                    self.next_button_check = time_now + self.button_repeat_delay_secs
                    for listener in self.listeners:
                        listener(index)
