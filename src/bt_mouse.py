import time
import logging

logger = logging.getLogger(__name__)

def check_button(button):
    if button >= 16:
        logger.warn("Button %d out of range", button)
        return False
    return True

def bound(value, minimum, maximum):
    return max(min(value, maximum), minimum)

class BluetoothMouse(object):
    def __init__(self, hid_device):
        self.hid_device = hid_device
        self.active_buttons = set()

    def button_down(self, button):
        if not check_button(button): return
        self.active_buttons.add(button)
        self.send_report()

    def button_up(self, button):
        if not check_button(button): return
        if button in self.active_buttons:
            self.active_buttons.remove(button)
        self.send_report()

    def click(self, button):
        if not check_button(button): return
        self.button_down(button)
        time.sleep(0.1)
        self.button_up(button)

    def move(self, dx=0, dy=0):
        dx = bound(dx, -32767, 32767)
        dy = bound(dy, -32767, 32767)
        self.send_report(dx, dy)

    def wheel(self, dv=0, dh=0):
        dv = bound(dv, -127, 127)
        dh = bound(dh, -127, 127)
        self.send_report(0, 0, dv, dh)

    def send_report(self, dx=0, dy=0, dv=0, dh=0):
        buttons = 0x0
        for button in self.active_buttons:
            buttons |= 1 << button
        message = bytes([0xa1, 0x03, buttons & 0xff, (buttons & 0xff00) >> 8,
                         dx & 0xff, (dx & 0xff00) >> 8, dy & 0xff, (dy & 0xff00) >> 8,
                         dv & 0xff, dh & 0xff])
        self.hid_device.send_interrupt_message(message)
