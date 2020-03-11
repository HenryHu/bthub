#!/usr/bin/env python3

from libinput import LibInput
from libinput.constant import Event, DeviceCapability, PointerAxis
import sys

li = LibInput(udev=True)
li.udev_assign_seat('seat0')

devices = {}

while True:
    got_event = False
    try:
        for event in li.get_event(timeout=0.001):
            got_event = True
            if event.type == Event.DEVICE_ADDED:
                dev = event.get_device()
                dev_type = ''
                if dev.has_capability(DeviceCapability.KEYBOARD):
                    dev_type += '+keyboard'
                if dev.has_capability(DeviceCapability.POINTER):
                    dev_type += '+mouse'
                print("Added:", dev.get_name(), dev_type)
                devices[dev.get_sysname()] = dev
    except RuntimeError:
        if got_event:
            continue
        else:
            break

while True:
    for event in li.get_event():
        type = event.type
        if type == Event.KEYBOARD_KEY:
            kbd_event = event.get_keyboard_event()
            print(kbd_event.get_key(), kbd_event.get_key_state())
        elif type == Event.POINTER_MOTION:
            motion_event = event.get_pointer_event()
            print(motion_event.get_dx(), motion_event.get_dy())
        elif type == Event.POINTER_BUTTON:
            button_event = event.get_pointer_event()
            print(button_event.get_button(), button_event.get_button_state())
        elif type == Event.POINTER_AXIS:
            axis_event = event.get_pointer_event()
            for axis in [PointerAxis.SCROLL_VERTICAL, PointerAxis.SCROLL_HORIZONTAL]:
                if axis_event.has_axis(axis):
                    print(axis_event.get_axis_source(), axis_event.get_axis_value(axis))
