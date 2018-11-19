#!/usr/bin/env python

import creds
import json
import paho.mqtt.client as mqtt
import uuid
import time

uuid = str(uuid.uuid4())

request = {"kind": "rpc_request",
           "args": {"label": uuid},
           "body": [{"kind": "take_photo", "args": {}}]}

def on_connect(client, userdata, flags, rc):
  # subscribe to rpc_ok for the message we are about to send
  client.subscribe("bot/" + creds.device_id + "/from_device")
  # subscribe to log to watch for image upload (Clumsy)
  client.subscribe("bot/" + creds.device_id + "/logs")
  # send take_photo request immediately
  client.publish("bot/" + creds.device_id + "/from_clients", json.dumps(request))

received_ack = False
image_filename = ""

def on_message(client, userdata, msg):
  resp = json.loads(msg.payload)
  if msg.topic.endswith("/from_device"):
    if resp['kind'] == 'rpc_ok':
      if resp['args']['label'] == uuid:
        global received_ack
        received_ack = True
    else:
      raise Exception(str(resp))
  else:  # log
    if resp['message'].startswith("Uploading:"):
      global image_filename
      image_filename = resp['message'].replace("Uploading: ", "")

client = mqtt.Client()
client.username_pw_set(creds.device_id, creds.token)
client.on_connect = on_connect
client.on_message = on_message
client.connect("brisk-bear.rmq.cloudamqp.com", 1883, 60)
client.loop_start()

retries = 10
return_code = 0
while True:
  if received_ack:
    break
  retries -= 1
  if retries == 0:
    print("TIMEOUT")
    return_code = 1
    break
  time.sleep(1)

client.disconnect()
client.loop_stop()

print("image uploaded as [%s]" % image_filename)
exit(return_code)
