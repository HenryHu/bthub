#!/usr/bin/env python3

from libinput import LibInput
from libinput.constant import Event, DeviceCapability, PointerAxis, KeyState, ButtonState
import sys
import logging

logger = logging.getLogger(__name__)

class Input(object):
    def __init__(self):
        self.li = LibInput(udev=True)
        self.li.udev_assign_seat('seat0')
        self.collect_devices()
        self.key_callback = None
        self.mouse_move_callback = None
        self.mouse_button_callback = None
        self.mouse_wheel_callback = None
        self.event_handlers = {
            Event.KEYBOARD_KEY: self.handle_key_event,
            Event.POINTER_MOTION: self.handle_pointer_motion,
            Event.POINTER_BUTTON: self.handle_pointer_button,
            Event.POINTER_AXIS: self.handle_pointer_axis,
        }

    def collect_devices(self):
        self.devices = {}
        while True:
            got_event = False
            try:
                for event in self.li.get_event(timeout=0.001):
                    got_event = True
                    if event.type == Event.DEVICE_ADDED:
                        dev = event.get_device()
                        dev_type = ''
                        if dev.has_capability(DeviceCapability.KEYBOARD):
                            dev_type += '+keyboard'
                        if dev.has_capability(DeviceCapability.POINTER):
                            dev_type += '+mouse'
                        logger.info("Device added: %s %s", dev.get_name(), dev_type)
                        self.devices[dev.get_sysname()] = dev
            except RuntimeError:
                if not got_event: break

    def register_callbacks(self, key_callback, mouse_move_callback,
                           mouse_button_callback, mouse_wheel_callback):
        self.key_callback = key_callback
        self.mouse_move_callback = mouse_move_callback
        self.mouse_button_callback = mouse_button_callback
        self.mouse_wheel_callback = mouse_wheel_callback

    def handle_key_event(self, event):
        kbd_event = event.get_keyboard_event()
        if self.key_callback:
            self.key_callback(kbd_event.get_key(),
                                kbd_event.get_key_state() == KeyState.PRESSED)

    def handle_pointer_motion(self, event):
        motion_event = event.get_pointer_event()
        if self.mouse_move_callback:
            self.mouse_move_callback(motion_event.get_dx(),
                                        motion_event.get_dy())

    def handle_pointer_button(self, event):
        button_event = event.get_pointer_event()
        if self.mouse_button_callback:
            self.mouse_button_callback(
                button_event.get_button(),
                button_event.get_button_state() == ButtonState.PRESSED)

    def handle_pointer_axis(self, event):
        axis_event = event.get_pointer_event()
        if not self.mouse_wheel_callback: return
        if axis_event.has_axis(PointerAxis.SCROLL_VERTICAL):
            self.mouse_wheel_callback(
                axis_event.get_axis_value(PointerAxis.SCROLL_VERTICAL), 0)
        if axis_event.has_axis(PointerAxis.SCROLL_HORIZONTAL):
            self.mouse_wheel_callback(
                0, axis_event.get_axis_value(PointerAxis.SCROLL_HORIZONTAL))

    def run(self):
        while True:
            for event in self.li.get_event():
                self.handle_event(event)

    def handle_event(self, event):
        if event.type in self.event_handlers:
            self.event_handlers[event.type](event)

if __name__ == "__main__":
    dev = Input()
    key = lambda key, state: print("Key press:", key, state)
    move = lambda dx, dy: print("Mouse move:", dx, dy)
    button = lambda button, state: print("Mouse button:", button, state)
    wheel = lambda dv, dh: print("Mouse wheel:", dv, dh)
    dev.register_callbacks(key, move, button, wheel)
    dev.run()
