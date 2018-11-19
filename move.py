#!/usr/bin/env python

import argparse
import creds
import json
import paho.mqtt.client as mqtt
import uuid
import time

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-x', type=int)
parser.add_argument('-y', type=int)
parser.add_argument('-z', type=int)
opts = parser.parse_args()

uuid = str(uuid.uuid4())

def coord(x, y, z):
  return {"kind": "coordinate", "args": {"x": x, "y": y, "z": z}}

move_request = {
    "kind":"rpc_request",
    "args":{"label": uuid},
    "body":[{"kind": "move_absolute",
             "args": {"location": coord(opts.x, opts.y, opts.z),
                      "offset": coord(0, 0, 0),
                      "speed": 100}}]}

def on_connect(client, userdata, flags, rc):
  # subscribe to rpc_ok for the message we are about to send
  client.subscribe("bot/" + creds.device_id + "/from_device")
  # send move message immediately
  client.publish("bot/" + creds.device_id + "/from_clients", json.dumps(move_request))

received_ack = False
def on_message(client, userdata, msg):
  global received_ack
  resp = json.loads(msg.payload)
  if resp['kind'] == 'rpc_ok':
    if resp['args']['label'] == uuid:
      received_ack = True
  else:
    raise Exception(str(resp))

client = mqtt.Client()
client.username_pw_set(creds.device_id, creds.token)
client.on_connect = on_connect
client.on_message = on_message
client.connect("brisk-bear.rmq.cloudamqp.com", 1883, 60)
client.loop_start()

retries = 20
return_code = 0
while True:
  if received_ack:
    print("move to", opts.x, opts.y, opts.z, "successful")
    break
  retries -= 1
  if retries == 0:
    print("TIMEOUT")
    return_code = 1
    break
  time.sleep(1)

client.disconnect()
client.loop_stop()

exit(return_code)
