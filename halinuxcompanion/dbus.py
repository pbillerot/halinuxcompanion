from dbus_next.aio import MessageBus, ProxyInterface
from dbus_next import BusType
from dbus_next.errors import DBusError
from typing import Callable, Optional
import logging

logger = logging.getLogger(__name__)

NOTIFICATIONS_INTERFACE = "org.freedesktop.Notifications"
LOGIN_INTERFACE = "org.freedesktop.login1.Manager"
SCREENSAVER_INTERFACE = "org.freedesktop.ScreenSaver"
SCREENSAVER_GNOME_INTERFACE = "org.gnome.ScreenSaver"

SIGNALS = {
    "session.notification_on_action_invoked": {
        "name": "on_action_invoked",
        "interface": NOTIFICATIONS_INTERFACE,
    },
    "session.notification_on_notification_closed": {
        "name": "on_notification_closed",
        "interface": NOTIFICATIONS_INTERFACE,
    },
    "session.screensaver_on_active_changed": {
        "name": "on_active_changed",
        "interface": SCREENSAVER_INTERFACE,
    },
    "session.gnome_screensaver_on_active_changed": {
        "name": "on_active_changed",
        "interface": SCREENSAVER_GNOME_INTERFACE,
    },
    "system.login_on_prepare_for_sleep": {
        "name": "on_prepare_for_sleep",
        "interface": LOGIN_INTERFACE,
    },
    "system.login_on_prepare_for_shutdown": {
        "name": "on_prepare_for_shutdown",
        "interface": LOGIN_INTERFACE,
    },
    "subscribed": [],
}

INTERFACES = {
    LOGIN_INTERFACE: {
        "type": "system",
        "service": "org.freedesktop.login1",
        "path": "/org/freedesktop/login1",
        "interface": LOGIN_INTERFACE,
    },
    SCREENSAVER_INTERFACE: {
        "type": "session",
        "service": SCREENSAVER_INTERFACE,
        "path": "/org/freedesktop/ScreenSaver",
        "interface": SCREENSAVER_INTERFACE,
    },
    SCREENSAVER_GNOME_INTERFACE: {
        "type": "session",
        "service": SCREENSAVER_GNOME_INTERFACE,
        "path": "/org/gnome/ScreenSaver",
        "interface": SCREENSAVER_GNOME_INTERFACE,
    },
    NOTIFICATIONS_INTERFACE: {
        "type": "session",
        "service": NOTIFICATIONS_INTERFACE,
        "path": "/org/freedesktop/Notifications",
        "interface": NOTIFICATIONS_INTERFACE,
    },
}


async def get_interface(bus, service, path, interface) -> Optional[ProxyInterface]:
    try:
        introspection = await bus.introspect(service, path)
        proxy = bus.get_proxy_object(service, path, introspection)
        return proxy.get_interface(interface)
    except DBusError:
        return None


class Dbus:
    session: MessageBus
    system: MessageBus
    interfaces: dict[str, ProxyInterface] = {}

    async def init(self) -> None:
        self.system = await MessageBus(bus_type=BusType.SYSTEM).connect()
        self.session = await MessageBus(bus_type=BusType.SESSION).connect()

    async def get_interface(self, name: str) -> Optional[ProxyInterface]:
        i = INTERFACES[name]
        bus_type, service, path, interface = i["type"], i["service"], i["path"], i["interface"]
        iface = self.interfaces.get(name)
        if iface is None:
            if bus_type == "system":
                bus = self.system
            else:
                bus = self.session
            iface = await get_interface(bus, service, path, interface)
            if iface is not None:
                self.interfaces[name] = iface

        return iface

    async def register_signal(self, signal_alias: str, callback: Callable) -> None:
        """Register a signal handler"""
        iface_name, signal_name = SIGNALS[signal_alias]["interface"], SIGNALS[signal_alias]["name"]
        iface = await self.get_interface(iface_name)
        if iface is not None:
            getattr(iface, signal_name)(callback)
            logger.info("Registered signal callback for interface:%s, signal:%s", iface_name, signal_name)
            SIGNALS["subscribed"].append((signal_alias, callback))
        else:
            logger.warning("Could not register signal callback for interface:%s, signal:%s", iface_name, signal_name)
