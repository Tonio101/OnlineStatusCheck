#!/usr/bin/env python3
import argparse
import json
import logging
import os
import sys

from time import sleep
from devices import Device
from mqtt_client import MQTTClient
from logger import Logger
log = Logger.getInstance().getLogger()

DELAY = (10 * 60) # Default to 10 min.


def parse_config_file(fname: str) -> dict:
    with open(os.path.abspath(fname), 'r') as fp:
        data = json.load(fp)
        return data


def configure_mqtt_client(config) -> MQTTClient:
    client = \
        MQTTClient(username=config['user'],
                   password=config['pasw'],
                   mqtt_host=config['host'],
                   mqtt_port=config['port'])
    return client


def configure_devices(config: dict) -> list:
    device_list = list()

    for device_info in config['devices']:
        device = Device(device_info=device_info)
        device_list.append(device)

    return device_list


def main(argv):
    usage = ("{FILE} --config <config_file> --debug").format(FILE=__file__)
    description = 'Check if hosts are up'
    parser = argparse.ArgumentParser(usage=usage, description=description)
    parser.add_argument("-c", "--config", help="Configuration file",
                        required=True)
    parser.add_argument("--debug", help="Enable verbose logging",
                        action='store_true', required=False)
    parser.set_defaults(debug=False)

    args = parser.parse_args()

    if args.debug:
        log.setLevel(logging.DEBUG)

    config = parse_config_file(args.config)
    log.debug(config)

    mqtt_broker_config = config['mqttBroker']

    mqtt_client = configure_mqtt_client(config=mqtt_broker_config)
    mqtt_client.connect_to_broker()

    device_list = configure_devices(config=config)
    log.debug(device_list)

    while True:
        for device in device_list:
            topic = device.get_mqtt_topic()
            result = device.ping_ok()
            mqtt_client.publish(topic, result)
            sleep(1)
        sleep(DELAY)


if __name__ == '__main__':
    main(sys.argv)
