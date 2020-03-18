import bt_profile
import logging
import bluetooth
import os
import dbus
import threading
import time

PORT_CONTROL = 17
PORT_INTERRUPT = 19

logger = logging.getLogger(__name__)

KEYBOARD_PROFILE_PATH = "/bthub/keyboard/profile"
SDP_RECORD_FILENAME = "sdp_record.xml"

# See https://www.bluetooth.com/specifications/assigned-numbers/service-discovery/
HID_SERVICE_UUID = "00001124-0000-1000-8000-00805f9b34fb"

class Receiver(object):
    def __init__(self, client_sock, close_callback=None):
        self.client = client_sock
        self.thread = threading.Thread(target=self.worker)
        self.close_callback = close_callback

    def start(self):
        logger.info("Starting receiver")
        self.thread.start()

    def worker(self):
        while True:
            msg = self.client.recv(4096)
            if not msg:
                break
            msg_type = msg[0]
            self.handler(msg_type, msg[1:])
        logger.info("Stopping receiver")
        if self.close_callback:
            self.close_callback()

    def close(self):
        self.client.close()

class ControlReceiver(Receiver):
    def handler(self, msg_type, data):
        logger.info("Got control msg %x %s", msg_type, data)

class InterruptReceiver(Receiver):
    def handler(self, msg_type, data):
        logger.info("Got interrupt msg %x %s", msg_type, data)
        if msg_type & 0xf0 == 0xa0:
            if msg_type & 0x0f != 0x02:
                logger.info("Invalid DATA msg: subtype != Output")
                return
            logger.info("Output: %s", data)

class BluetoothKeyboard(object):
    def __init__(self, data_dir):
        logger.info("Keyboard init")
        self.control_sock = None
        self.interrupt_sock = None
        self.control_client = None
        self.interrupt_client = None
        self.data_dir = data_dir

    def init(self):
        self.init_profile()

    def init_profile(self):
        """Register a profile to bluez.
        Details: https://github.com/pauloborges/bluez/blob/master/doc/profile-api.txt"""

        logger.info("Init bluez profile")

        options = {
            "Name": "bthub Virtual Keyboard",
            "ServiceRecord": self.get_service_record(),
            "Role": "server",
            "RequiredAuthentication": True,
            "RequiredAuthorization": True,
        }

        bus = dbus.SystemBus()
        profile = bt_profile.BluetoothKeyboardProfile(bus, KEYBOARD_PROFILE_PATH)

        bluez = bus.get_object("org.bluez", "/org/bluez")
        profile_manager = dbus.Interface(bluez, "org.bluez.ProfileManager1")
        profile_manager.RegisterProfile(KEYBOARD_PROFILE_PATH, HID_SERVICE_UUID, options)
        logger.info("Registered profile to bluez")

    def get_service_record(self):
        return open(os.path.join(self.data_dir, SDP_RECORD_FILENAME)).read()

    def listen(self):
        logger.info("Listening for connections")
        self.control_sock = bluetooth.BluetoothSocket(proto=bluetooth.L2CAP)
        self.control_sock.bind(("", PORT_CONTROL))
        self.control_sock.listen(1)

        self.interrupt_sock = bluetooth.BluetoothSocket(proto=bluetooth.L2CAP)
        self.interrupt_sock.bind(("", PORT_INTERRUPT))
        self.interrupt_sock.listen(1)

    def accept(self):
        logging.info("Accepting for connections")

        if self.control_client is not None:
            logger.error("Already accepted")
            return

        self.control_client, control_client_info = self.control_sock.accept()
        logging.info("Got control client: %r", control_client_info[0])

        self.interrupt_client, interrupt_client_info = self.interrupt_sock.accept()
        logging.info("Got interrupt client: %r", interrupt_client_info[0])

        self.control_client_receiver = ControlReceiver(self.control_client, self.client_closed)
        self.control_client_receiver.start()
        self.interrupt_client_receiver = InterruptReceiver(self.interrupt_client)
        self.interrupt_client_receiver.start()

    def close(self):
        if self.control_client:
            self.control_client.close()
            self.control_client = None
            self.control_client_receiver.close()
            self.control_client_receiver = None

        if self.interrupt_client:
            self.interrupt_client.close()
            self.interrupt_client = None
            self.interrupt_client_receiver.close()
            self.interrupt_client_receiver = None

    def client_closed(self):
        self.close()

    def send_key_state(self, modifier=0, key=0):
        # 0xA1: 0xA0 = DATA 0x01 = Input
        # 0x01: HID report ID
        message = bytes([0xa1, 0x01, 0x00, modifier, 0x00, key, 0x00, 0x00, 0x00, 0x00, 0x00])
        self.send_interrupt_message(message)

    def send_key(self, modifier, key):
        self.send_key_state(modifier, key)
        time.sleep(0.1)
        # Send a key up message, releasing all keys
        self.send_key_state()

    def send_interrupt_message(self, message):
        if not self.interrupt_client:
            raise RuntimeError("Must accept connection first")

        logger.info("Sending %r", message)
        self.interrupt_client.send(message)

    def send_mouse_click(self, buttons):
        self.send_mouse_state(0, 0, buttons, 0)
        time.sleep(0.1)
        self.send_mouse_state(0, 0, 0, 0)

    def send_mouse_move(self, dx=0, dy=0, buttons=0):
        self.send_mouse_state(dx, dy, buttons)

    def send_wheel(self, dv=0, dh=0):
        self.send_mouse_state(0, 0, 0, dv, dh)

    def send_mouse_state(self, dx=0, dy=0, buttons=0, dv=0, dh=0):
        message = bytes([0xa1, 0x03, buttons & 0xff, (buttons & 0xff00) >> 8,
                         dx & 0xff, (dx & 0xff00) >> 8, dy & 0xff, (dy & 0xff00) >> 8,
                         dv & 0xff, dh & 0xff])
        self.interrupt_client.send(message)
