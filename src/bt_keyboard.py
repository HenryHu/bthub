import time
import logging

logger = logging.getLogger(__name__)

def check_modifier(modifier):
    if modifier >= 8:
        logger.warn("Modifier %d out of range", modifier)
        return False
    return True


class BluetoothKeyboard(object):
    def __init__(self, hid_device):
        self.hid_device = hid_device
        self.active_modifiers = set()
        self.active_keys = set()

    def modifier_down(self, modifier):
        if not check_modifier(modifier): return
        self.active_modifiers.add(modifier)
        self.send_report()

    def modifier_up(self, modifier):
        if not check_modifier(modifier): return
        if modifier in self.active_modifiers:
            self.active_modifiers.remove(modifier)
        self.send_report()

    def key_down(self, key):
        self.active_keys.add(key)
        self.send_report()

    def key_up(self, key):
        if key in self.active_keys:
            self.active_keys.remove(key)
        self.send_report()

    def send_report(self):
        # 0xA1: 0xA0 = DATA 0x01 = Input
        # 0x01: HID report ID
        modifier = 0x0
        for modifier in self.active_modifiers:
            modifier |= 1 << modifier
        message = bytearray([0xa1, 0x01, 0x00, modifier, 0x00,
                             0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        key_index = 5 # 5 ~ 10
        for key in self.active_keys:
            if key_index < len(message):
                message[key_index] = key
                key_index += 1
            else:
                logger.warn("Too many key pressed, discarding %x", key)
        self.hid_device.send_interrupt_message(bytes(message))

    def key(self, modifier, key):
        if modifier is not None:
            self.modifier_down(modifier)
        self.key_down(key)
        time.sleep(0.1)
        self.key_up(key)
        if modifier is not None:
            self.modifier_up(modifier)

    def led(self, led):
        leds = []
        if led & 0x1:
            leds.append('NUM')
        if led & 0x2:
            leds.append('CAPS')
        if led & 0x4:
            leds.append('SCROLL')
        logger.info("LED: %x", ' '.join(leds))
