import subprocess, platform

from datetime import datetime
from mqtt_client import MQTTClient
from logger import Logger
log = Logger.getInstance().getLogger()


class Device(object):

    def __init__(self, device_info):
        self.type = device_info['type']
        self.name = device_info['name']
        self.host = device_info['host']
        self.device_id = device_info['deviceId']
        self.mqtt_topic = device_info['mqttTopic']

    def get_type(self) -> str:
        return self.type

    def get_name(self) -> str:
        return self.name

    def get_host(self) -> str:
        return self.host

    def get_device_id(self) -> str:
        return self.device_id

    def get_mqtt_topic(self) -> str:
        return self.mqtt_topic

    def get_current_time(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def set_mqtt_client(self, mqtt_client: MQTTClient):
        self.mqtt_client = mqtt_client

    def ping_ok(self) -> dict:
        try:
            output = \
                subprocess.check_output(
                    ("ping -{} 1 {}").format(
                        'c', self.host), shell=True)
            log.debug(output)
        except Exception as e:
            return {"pingOk": False}

        return {"pingOk": True}

    def __str__(self):
        to_str = ("Name: {}\n"
                  "Current Time: {}\n").format(
                    self.name,
                    self.get_current_time()
                  )

        return to_str
