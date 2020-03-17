import dbus
import dbus.service
import logging
import os
import collections

logger = logging.getLogger(__name__)

class BluetoothKeyboardProfile(dbus.service.Object):
    """Details: https://github.com/pauloborges/bluez/blob/master/doc/profile-api.txt"""

    def __init__(self, bus, path, release_callback=None):
        name = dbus.service.BusName("bthub.Keyboard", bus=bus)
        super().__init__(name, path)
        self.release_callback = release_callback
        self.device_fd_map = collections.defaultdict(set)
        logger.info("Registered keyboard profile at %s", path)

    @dbus.service.method("org.bluez.Profile1", in_signature="", out_signature="")
    def Release(self):
        logger.info("Release")
        if self.release_callback:
            self.release_callback()

    @dbus.service.method("org.bluez.Profile1", in_signature="oha{sv}", out_signature="")
    def NewConnection(self, device, fd, fd_properties):
        logger.info("New connection, fd = %r, device = %r", fd, device)
        self.device_fd_map[device].add(fd.take())

        for key, value in fd_properties.items():
            logger.info("%r = %r", key, value)

    @dbus.service.method("org.bluez.Profile1", in_signature="o", out_signature="")
    def RequestDisconnection(self, device):
        logger.info("RequestDisconnection, device = %r", device)
        for fd in self.device_fd_map[device]:
            os.close(fd)
        del self.device_fd_map[device]
