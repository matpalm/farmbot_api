#!/usr/bin/env python3

import creds
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
  # occasional status message
  client.subscribe("bot/" + creds.device_id + "/status")
  # log entries
  client.subscribe("bot/" + creds.device_id + "/logs")
  # request commands from client
  client.subscribe("bot/" + creds.device_id + "/from_clients")
  # responses
  client.subscribe("bot/" + creds.device_id + "/from_device")

def on_message(client, userdata, msg):
  print(msg.topic + " " + str(msg.payload))

client = mqtt.Client()
client.username_pw_set(creds.device_id, creds.token)
client.on_connect = on_connect
client.on_message = on_message
client.connect("brisk-bear.rmq.cloudamqp.com", 1883, 60)
client.loop_forever()
