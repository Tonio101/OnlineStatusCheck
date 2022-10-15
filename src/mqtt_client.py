import json
import time
import sys

import paho.mqtt.client as mqtt
from logger import Logger
log = Logger.getInstance().getLogger()


class MQTTClient(object):

    def __init__(self, username, password, mqtt_host, mqtt_port):
        self.host = mqtt_host
        self.port = mqtt_port
        self.lock = None
        self.topic = None
        self.input_queue = None

        self.client = mqtt.Client(client_id=self.generate_client_id(), clean_session=True,
                                  userdata=None, protocol=mqtt.MQTTv311,
                                  transport="tcp")
        self.client.username_pw_set(username, password)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def generate_client_id(self) -> str:
        """
        Each subscriber needs a unique id.

        Returns:
            str: unique id
        """
        return ("{}-{}").format(
            __name__,
            str(int(time.time()))
        )

    def set_input_queue(self, lock, input_queue):
        """
        Queue up the messages from the topic.

        Args:
            lock (Lock): Queue lock
            input_queue (Queue): Message queue
        """
        self.lock = lock
        self.input_queue = input_queue

    def set_event_topic(self, topic):
        """
        Set the topic

        Args:
            topic (str): Topic
        """
        self.topic = topic

    def connect_to_broker(self):
        """
        Connect to broker.
        """
        log.info("Connecting to broker...")
        self.client.connect(self.host, self.port, 10)
        # Spins a thread that will call the loop method at
        # regualr intervals and handle re-connects.
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        """
        On connect callback.

        Args:
            client (_type_): _description_
            userdata (_type_): _description_
            flags (_type_): _description_
            rc (_type_): _description_
        """
        log.info("Connected with result code %s" % rc)

        if (rc == 0):
            log.info("Successfully connected to broker %s" % self.host)
            if self.topic:
                self.client.subscribe(self.topic)
        else:
            log.error("Connection with result code %s" % rc)
            sys.exit(2)

    def on_message(self, client, userdata, msg):
        """
        On message callback.

        Args:
            client (_type_): _description_
            userdata (_type_): _description_
            msg (_type_): _description_
        """
        # payload = json.loads(msg.payload.decode("utf-8"))
        log.info(msg)

        if self.input_queue:
            self.lock.acquire()
            self.input_queue.put(msg)
            self.lock.release()
        else:
            log.info(json.loads(msg.payload.decode("utf-8")))

    def publish(self, topic: str, data: dict):
        """
        Publish a message to a topic.

        Args:
            topic (str): mqtt topic
            data (dict): message data

        Returns:
            _type_: _description_
        """
        rc = self.client.publish(topic, json.dumps(data))
        if rc[0] == 0:
            log.debug("Successfully published event to topic {0}".format(
                topic
            ))
        else:
            log.error("Failed to publish {0} to topic {1}".format(
                data, topic
            ))

        return rc[0]
