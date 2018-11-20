import paho.mqtt.client as mqtt
import json
import time
from uuid import uuid4

def coord(x, y, z):
  return {"kind": "coordinate", "args": {"x": x, "y": y, "z": z}}

def json_move_request(x, y, z):
  # return uuid for request as well as json request

  # TODO: decide speed 50 or 100; seeing more reliable moves, for short
  # distance, with speed 50... (???)
  uuid = str(uuid4())
  request = json.dumps({
    "kind": "rpc_request",
    "args": {"label": uuid},
    "body": [{"kind": "move_absolute",
              "args": {"location": coord(x, y, z),
                       "offset": coord(0, 0, 0),
                       "speed": 50}}]})
  return uuid, request

class FarmbotClient(object):

  def __init__(self, device_id, token):
    self.device_id = device_id
    self.client = mqtt.Client()
    self.client.username_pw_set(self.device_id, token)
    self.client.on_connect = self._on_connect
    self.client.on_message = self._on_message
    self.connected = False
    self.client.connect("brisk-bear.rmq.cloudamqp.com", 1883, 60)
    self.client.loop_start()

  def shutdown(self):
    self.client.disconnect()
    self.client.loop_stop()

  def move(self, x, y, z):
    print("> move")
    self._wait_for_connection()
    # issue request...
    self.pending_uuid, json_request = json_move_request(x, y, z)
    self.received_ack = False
    self.client.publish("bot/" + self.device_id + "/from_clients", json_request)
    # wait for ack
    while not self.received_ack:
#      print("waiting for ack for", self.pending_uuid)
      time.sleep(0.1)
    print("< move")

  def _wait_for_connection(self):
    # TODO: timeout.
    # TODO: better way to do all this async event driven rather than with polling :/
    if not self.connected:
      print("waiting to be connected")
      time.sleep(0.1)

  def _on_connect(self, client, userdata, flags, rc):
    print("> _on_connect")
    self.client.subscribe("bot/" + self.device_id + "/from_device")
    self.connected = True
    print("< _on_connect")

  def _on_message(self, client, userdata, msg):
    print("> _on_message", msg.payload)
    resp = json.loads(msg.payload)
    if resp['kind'] == 'rpc_ok':
      print("received rpc_ok msg", resp['args'])
      if resp['args']['label'] == self.pending_uuid:
        print("MATCH for pending uuid")
        self.received_ack = True
    print("< _on_message")
