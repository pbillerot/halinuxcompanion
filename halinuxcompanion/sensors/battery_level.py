from types import MethodType
from halinuxcompanion.sensor import Sensor
import psutil
import datetime as dt

BatteryLevel = Sensor()
BatteryLevel.config_name = "battery_level"
BatteryLevel.attributes = {
        "time_left": "",
}

BatteryLevel.device_class = "battery"
BatteryLevel.state_class = "measurement"
BatteryLevel.icon = "mdi:battery"
BatteryLevel.name = "Battery Level"
BatteryLevel.state = "unavailable"
BatteryLevel.type = "sensor"
BatteryLevel.unique_id = "battery_level"
BatteryLevel.unit_of_measurement = "%"


def updater_old(self):
    data = psutil.sensors_battery()
    if data is not None:
        minutes, seconds = divmod(data.secsleft, 60)
        hours, minutes = divmod(minutes, 60)

        self.state = round(data.percent)
        self.icon = "mdi:battery-%d0" % round(data.percent / 10)
        self.attributes["time_left"] = "%d:%02d:%02d" % (hours, minutes, seconds)

def updater(self):
    try:
        f = open('/sys/class/power_supply/BAT0/capacity')
        bat0 = round(int(f.read().strip('\n')))
        f.close()
        f = open('/sys/class/power_supply/BAT1/capacity')
        bat1 = round(int(f.read().strip('\n')))
        f.close()
        data = round((bat0 + bat1)/2)
        data = round(bat0)
        if data is not None:
            self.state = data
            self.icon = "mdi:battery-%d0" % round(data / 10)
            self.attributes["time_left"] = dt.datetime.now().strftime('%H:%M %D')
    except Exception as inst:
        print(inst)

BatteryLevel.updater = MethodType(updater, BatteryLevel)

