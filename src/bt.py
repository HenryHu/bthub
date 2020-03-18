#!/usr/bin/env python3

import dbus.mainloop.glib
import threading
import bt_hid
import gi
import logging
import os
import sys
from gi.repository import GLib

logger = logging.getLogger(__name__)

class App(object):
    def __init__(self):
        self.hid_device = None

    def start(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

        self.hid_device = bt_hid.BluetoothHID(sys.path[0])
        self.hid_device.init()
        self.hid_device.listen()

        self.start_console()

        #self.mainloop = gobject.MainLoop()
        #dbus.set_default_main_loop(mainloop)
        #self.mainloop.run()
        #Gtk.main()

        self.mainloop = GLib.MainLoop()
        self.mainloop.run()

    def start_console(self):
        self.console_thread = threading.Thread(target=self.console_handler)
        self.console_thread.start()

    def console_handler(self):
        while True:
            user_input = input("bt > ")
            if ' ' in user_input:
                cmd, args = user_input.split(' ', 1)
            else:
                cmd = user_input
                args = None

            if cmd == 'accept':
                self.hid_device.accept()
            if cmd == 'close':
                self.hid_device.close()
            if cmd == 'key':
                if args is None:
                    logger.error("Arg missing")
                    continue
                self.hid_device.keyboard.key(None, int(args))
            if cmd == 'click':
                self.hid_device.mouse.click(int(args))
            if cmd == 'move':
                (arg1, arg2) = args.split(' ')
                self.hid_device.mouse.move(int(arg1), int(arg2))
            if cmd == 'wheel':
                (arg1, arg2) = args.split(' ')
                self.hid_device.mouse.wheel(int(args1), int(arg2))
            if cmd == 'quit':
                self.mainloop.quit()
                break


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if not os.geteuid() == 0:
        logger.error("Need root permission")
        sys.exit(1)

    app = App()
    app.start()
