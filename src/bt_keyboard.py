import time
import logging

logger = logging.getLogger(__name__)

def check_modifier(modifier):
    if modifier >= 8:
        logger.warn("Modifier %d out of range", modifier)
        return False
    return True

MEDIA_KEY_REPORT_POS = {
    0x0223: 0x01, # Home
    0x0221: 0x02, # Search
    0x01b1: 0x04, # Screensaver
    0xb7: 0x08, # Stop
    0xb6: 0x10, # Previous
    0xcd: 0x20, # Play/Pause
    0xb5: 0x40, # Next
    0xe2: 0x80, # Mute
    0xea: 0x0100, # Vol down
    0xe9: 0x0200, # Vol up
    0x30: 0x0400, # Power
}

def add_media_key_to_data(media_key, data):
    pos = MEDIA_KEY_REPORT_POS.get(media_key, None)
    if pos is None:
        logger.warning("Unknown media key: %x", media_key)
        return data
    return data | pos


class BluetoothKeyboard(object):
    def __init__(self, hid_device):
        self.hid_device = hid_device
        self.active_modifiers = set()
        self.active_keys = set()
        self.active_media_keys = set()

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

    def media_key_down(self, key):
        self.active_media_keys.add(key)
        self.send_media_report()

    def media_key_up(self, key):
        if key in self.active_media_keys: self.active_media_keys.remove(key)
        self.send_media_report()

    def send_report(self):
        # 0xA1: 0xA0 = DATA 0x01 = Input
        # 0x01: HID report ID
        modifier_byte = 0x0
        for modifier in self.active_modifiers:
            modifier_byte |= 1 << modifier
        message = bytearray([0xa1, 0x01, modifier_byte, 0x00,
                             0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        key_index = 5 # 5 ~ 10
        for key in self.active_keys:
            if key_index < len(message):
                message[key_index] = key
                key_index += 1
            else:
                logger.warn("Too many key pressed, discarding %x", key)
        self.hid_device.send_interrupt_message(bytes(message))

    def send_media_report(self):
        # 0xA1: 0xA0 = DATA 0x01 = Input
        # 0x02: HID report ID
        data = 0x0000
        for media_key in self.active_media_keys:
            data = add_media_key_to_data(media_key, data)
        message = bytearray([0xa1, 0x02, data & 0xff, data >> 8, 0x00])
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
        logger.info("LED: %s", ' '.join(leds))

    def clear(self):
        self.active_keys.clear()
        self.active_modifiers.clear()
        self.send_report()
