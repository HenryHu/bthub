#!/usr/bin/env python3

import dbus.mainloop.glib
import threading
import bt_keyboard
import gi
import logging
import os
import sys
from gi.repository import GLib

logger = logging.getLogger(__name__)

class App(object):
    def __init__(self):
        self.keyboard = None

    def start(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

        self.keyboard = bt_keyboard.BluetoothKeyboard(sys.path[0])
        self.keyboard.init()
        self.keyboard.listen()

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
                self.keyboard.accept()
            if cmd == 'close':
                self.keyboard.close()
            if cmd == 'send':
                if args is None:
                    logger.error("Arg missing")
                    continue
                self.keyboard.send_key(0, int(args))
            if cmd == 'click':
                self.keyboard.send_mouse_click(int(args))
            if cmd == 'move':
                (arg1, arg2) = args.split(' ')
                self.keyboard.send_mouse_move(int(arg1), int(arg2))
            if cmd == 'wheel':
                self.keyboard.send_wheel(int(args))
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
