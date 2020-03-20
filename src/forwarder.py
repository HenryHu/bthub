#!/usr/bin/env python3

import logging
import input
import bt_hid
from libinput.evcodes import Key, Button
import dbus.mainloop.glib
import gi
from gi.repository import GLib
import threading

logger = logging.getLogger(__name__)

MODIFIER_CODES = {
    Key.KEY_LEFTCTRL: 0,
    Key.KEY_LEFTSHIFT: 1,
    Key.KEY_LEFTALT: 2,
    Key.KEY_LEFTMETA: 3,
    Key.KEY_RIGHTCTRL: 4,
    Key.KEY_RIGHTSHIFT: 5,
    Key.KEY_RIGHTALT: 6,
    Key.KEY_RIGHTMETA: 7,
}

KEY_CODES = {
    Key.KEY_A: 0x04,
    Key.KEY_B: 0x05,
    Key.KEY_C: 0x06,
    Key.KEY_D: 0x07,
    Key.KEY_E: 0x08,
    Key.KEY_F: 0x09,
    Key.KEY_G: 0x0a,
    Key.KEY_H: 0x0b,
    Key.KEY_I: 0x0c,
    Key.KEY_J: 0x0d,
    Key.KEY_K: 0x0e,
    Key.KEY_L: 0x0f,
    Key.KEY_M: 0x10,
    Key.KEY_N: 0x11,
    Key.KEY_O: 0x12,
    Key.KEY_P: 0x13,
    Key.KEY_Q: 0x14,
    Key.KEY_R: 0x15,
    Key.KEY_S: 0x16,
    Key.KEY_T: 0x17,
    Key.KEY_U: 0x18,
    Key.KEY_V: 0x19,
    Key.KEY_W: 0x1a,
    Key.KEY_X: 0x1b,
    Key.KEY_Y: 0x1c,
    Key.KEY_Z: 0x1d,
    Key.KEY_1: 0x1e,
    Key.KEY_2: 0x1f,
    Key.KEY_3: 0x20,
    Key.KEY_4: 0x21,
    Key.KEY_5: 0x22,
    Key.KEY_6: 0x23,
    Key.KEY_7: 0x24,
    Key.KEY_8: 0x25,
    Key.KEY_9: 0x26,
    Key.KEY_0: 0x27,
    Key.KEY_ENTER: 0x28,
    Key.KEY_ESC: 0x29,
    Key.KEY_BACKSPACE: 0x2a,
    Key.KEY_TAB: 0x2b,
    Key.KEY_SPACE: 0x2c,
    Key.KEY_MINUS: 0x2d,
    Key.KEY_EQUAL: 0x2e,
    Key.KEY_LEFTBRACE: 0x2f,
    Key.KEY_RIGHTBRACE: 0x30,
    Key.KEY_BACKSLASH: 0x31,
    # Key.KEY_HASHTILDE: 0x32,
    Key.KEY_SEMICOLON: 0x33,
    Key.KEY_APOSTROPHE: 0x34,
    Key.KEY_GRAVE: 0x35,
    Key.KEY_COMMA: 0x36,
    Key.KEY_DOT: 0x37,
    Key.KEY_SLASH: 0x38,
    Key.KEY_CAPSLOCK: 0x39,
    Key.KEY_F1: 0x3a,
    Key.KEY_F2: 0x3b,
    Key.KEY_F3: 0x3c,
    Key.KEY_F4: 0x3d,
    Key.KEY_F5: 0x3e,
    Key.KEY_F6: 0x3f,
    Key.KEY_F7: 0x40,
    Key.KEY_F8: 0x41,
    Key.KEY_F9: 0x42,
    Key.KEY_F10: 0x43,
    Key.KEY_F11: 0x44,
    Key.KEY_F12: 0x45,
    Key.KEY_SYSRQ: 0x46,
    Key.KEY_SCROLLLOCK: 0x47,
    Key.KEY_PAUSE: 0x48,
    Key.KEY_INSERT: 0x49,
    Key.KEY_HOME: 0x4a,
    Key.KEY_PAGEUP: 0x4b,
    Key.KEY_DELETE: 0x4c,
    Key.KEY_END: 0x4d,
    Key.KEY_PAGEDOWN: 0x4e,
    Key.KEY_RIGHT: 0x4f,
    Key.KEY_LEFT: 0x50,
    Key.KEY_DOWN: 0x51,
    Key.KEY_UP: 0x52,
    Key.KEY_NUMLOCK: 0x53,
    Key.KEY_KPSLASH: 0x54,
    Key.KEY_KPASTERISK: 0x55,
    Key.KEY_KPMINUS: 0x56,
    Key.KEY_KPPLUS: 0x57,
    Key.KEY_KPENTER: 0x58,
    Key.KEY_KP1: 0x59,
    Key.KEY_KP2: 0x5a,
    Key.KEY_KP3: 0x5b,
    Key.KEY_KP4: 0x5c,
    Key.KEY_KP5: 0x5d,
    Key.KEY_KP6: 0x5e,
    Key.KEY_KP7: 0x5f,
    Key.KEY_KP8: 0x60,
    Key.KEY_KP9: 0x61,
    Key.KEY_KP0: 0x62,
    Key.KEY_KPDOT: 0x63,
    Key.KEY_102ND: 0x64,
    Key.KEY_COMPOSE: 0x65,
    Key.KEY_POWER: 0x66,
    Key.KEY_KPEQUAL: 0x67,
    Key.KEY_F13: 0x68,
    Key.KEY_F14: 0x69,
    Key.KEY_F15: 0x6a,
    Key.KEY_F16: 0x6b,
    Key.KEY_F17: 0x6c,
    Key.KEY_F18: 0x6d,
    Key.KEY_F19: 0x6e,
    Key.KEY_F20: 0x6f,
    Key.KEY_F21: 0x70,
    Key.KEY_F22: 0x71,
    Key.KEY_F23: 0x72,
    Key.KEY_F24: 0x73,
    Key.KEY_OPEN: 0x74,
    Key.KEY_HELP: 0x75,
    Key.KEY_PROPS: 0x76,
    Key.KEY_FRONT: 0x77,
    Key.KEY_STOP: 0x78,
    Key.KEY_AGAIN: 0x79,
    Key.KEY_UNDO: 0x7a,
    Key.KEY_CUT: 0x7b,
    Key.KEY_COPY: 0x7c,
    Key.KEY_PASTE: 0x7d,
    Key.KEY_FIND: 0x7e,
    Key.KEY_MUTE: 0x7f,
    Key.KEY_VOLUMEUP: 0x80,
    Key.KEY_VOLUMEDOWN: 0x81,
    Key.KEY_KPCOMMA: 0x85,
    Key.KEY_RO: 0x87,
    Key.KEY_KATAKANAHIRAGANA: 0x88,
    Key.KEY_YEN: 0x89,
    Key.KEY_HENKAN: 0x8a,
    Key.KEY_MUHENKAN: 0x8b,
    Key.KEY_KPJPCOMMA: 0x8c,
    Key.KEY_HANGEUL: 0x90,
    Key.KEY_HANJA: 0x91,
    Key.KEY_KATAKANA: 0x92,
    Key.KEY_HIRAGANA: 0x93,
    Key.KEY_ZENKAKUHANKAKU: 0x94,
    Key.KEY_KPLEFTPAREN: 0xb6,
    Key.KEY_KPRIGHTPAREN: 0xb7,
    #Key.KEY_MEDIA_PLAYPAUSE: 0xe8,
    #Key.KEY_MEDIA_STOPCD: 0xe9,
    #Key.KEY_MEDIA_PREVIOUSSONG: 0xea,
    #Key.KEY_MEDIA_NEXTSONG: 0xeb,
    #Key.KEY_MEDIA_EJECTCD: 0xec,
    #Key.KEY_MEDIA_VOLUMEUP: 0xed,
    #Key.KEY_MEDIA_VOLUMEDOWN: 0xee,
    #Key.KEY_MEDIA_MUTE: 0xef,
    #Key.KEY_MEDIA_WWW: 0xf0,
    #Key.KEY_MEDIA_BACK: 0xf1,
    #Key.KEY_MEDIA_FORWARD: 0xf2,
    #Key.KEY_MEDIA_STOP: 0xf3,
    #Key.KEY_MEDIA_FIND: 0xf4,
    #Key.KEY_MEDIA_SCROLLUP: 0xf5,
    #Key.KEY_MEDIA_SCROLLDOWN: 0xf6,
    #Key.KEY_MEDIA_EDIT: 0xf7,
    #Key.KEY_MEDIA_SLEEP: 0xf8,
    #Key.KEY_MEDIA_COFFEE: 0xf9,
    #Key.KEY_MEDIA_REFRESH: 0xfa,
    #Key.KEY_MEDIA_CALC: 0xfb,
}

BUTTON_CODES = {
    Button.BTN_MOUSE: 0,
    Button.BTN_RIGHT: 1,
    Button.BTN_MIDDLE: 2,
    Button.BTN_SIDE: 3,
    Button.BTN_EXTRA: 4,
}

def get_modifier_code(key):
    return MODIFIER_CODES.get(key, None)

def get_key_code(key):
    return KEY_CODES.get(key, None)

def get_button_code(button):
    return BUTTON_CODES.get(button, None)

def has_switch_keys(active_keys):
    return Key.KEY_RIGHTCTRL in active_keys and Key.KEY_PAUSE in active_keys

class Forwarder(object):
    def __init__(self, data_path):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.input_device = input.Input()
        self.hid_device = bt_hid.BluetoothHID(data_path)
        self.hid_device.init()
        self.input_device.register_callbacks(
            self.key_callback, self.mouse_move_callback,
            self.mouse_button_callback, self.mouse_wheel_callback)
        self.clients = {}
        self.client = None
        self.active_keys = set()
        self.ignore_keys = set()

    def key_callback(self, key, down):
        if down:
            self.active_keys.add(key)
        else:
            if key in self.active_keys: self.active_keys.remove(key)
        if self.ignore_keys:
            if key in self.ignore_keys:
                self.ignore_keys.remove(key)
            return
        if has_switch_keys(self.active_keys):
            logger.info("Switching client")
            self.switch_client()
            self.ignore_keys.clear()
            self.ignore_keys.update(self.active_keys)
            return
        if self.client is None:
            logger.warning("Discard event, not connected")
            return
        modifier_code = get_modifier_code(key)
        if modifier_code is not None:
            if down:
                self.client.keyboard.modifier_down(modifier_code)
            else:
                self.client.keyboard.modifier_up(modifier_code)
        else:
            key_code = get_key_code(key)
            if key_code is None:
                logger.warning("Unknown key: %r", key)
                return
            if down:
                self.client.keyboard.key_down(key_code)
            else:
                self.client.keyboard.key_up(key_code)

    def mouse_move_callback(self, dx, dy):
        if self.client is None:
            logger.warning("Discard event, not connected")
            return
        self.client.mouse.move(int(dx), int(dy))

    def mouse_button_callback(self, button, down):
        if self.client is None:
            logger.warning("Discard event, not connected")
            return
        button_code = get_button_code(button)
        if button_code is None:
            logger.warning("Unknown button: %r", button)
            return
        if down:
            self.client.mouse.button_down(button_code)
        else:
            self.client.mouse.button_up(button_code)

    def mouse_wheel_callback(self, dv, dh):
        if self.client is None:
            logger.warning("Discard event, not connected")
            return
        self.client.mouse.wheel(-int(dv / 5), -int(dh / 5))

    def wait_client(self):
        while True:
            client = self.hid_device.accept(self.client_closed)
            self.clients[client.get_remote_address()] = client
            if self.client is None:
                self.client = client

    def client_closed(self, remote_address):
        if remote_address in self.clients:
            del self.clients[remote_address]
            if self.client and self.client.get_remote_address() == remote_address:
                self.client = None
                self.switch_client()
        else:
            logger.error("Unknown client %s closed", remote_address)

    def switch_client(self):
        if not self.clients:
            logger.warning("No client to switch to")
            return
        client_addresses = list(self.clients.keys())
        if self.client is None:
            client_index = -1
        else:
            self.client.keyboard.clear()
            self.client.mouse.clear()
            client_index = client_addresses.index(self.client.get_remote_address())
        client_index = (client_index + 1) % len(client_addresses)
        new_address = client_addresses[client_index]
        logger.info("Switching to %s", new_address)
        self.client = self.clients[new_address]

    def run(self):
        self.hid_device.listen()
        self.wait_client_thread = threading.Thread(target=self.wait_client)
        self.wait_client_thread.daemon = True
        self.wait_client_thread.start()
        self.forward_thread = threading.Thread(target=self.input_device.run)
        self.forward_thread.daemon = True
        self.forward_thread.start()
        self.mainloop = GLib.MainLoop()
        self.mainloop.run()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    import sys
    forwarder = Forwarder(sys.path[0])
    forwarder.run()
