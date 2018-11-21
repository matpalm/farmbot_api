import paho.mqtt.client as mqtt
import json
import time
from uuid import uuid4

def coord(x, y, z):
  return {"kind": "coordinate", "args": {"x": x, "y": y, "z": z}}

def move_request(x, y, z):
  return {"kind": "rpc_request",
          "args": {"label": str(uuid4())},
          "body": [{"kind": "move_absolute",
                    "args": {"location": coord(x, y, z),
                             "offset": coord(0, 0, 0),
                             "speed": 50}}]}

def take_photo_request():
  return {"kind": "rpc_request",
          "args": {"label": str(uuid4())},
          "body": [{"kind": "take_photo", "args": {}}]}

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
    self._blocking_request(move_request(x, y, z))
    print("< move")

  def take_photo(self):
    # TODO: is this enough? it's issue a request for the photo, but is the actual capture async?
    print("> take photo")
    self._blocking_request(take_photo_request())
    print("< take photo")

  def _blocking_request(self, request):
    self._wait_for_connection()
    self.pending_uuid = request['args']['label']
    self.received_ack = False
    self.client.publish("bot/" + self.device_id + "/from_clients", json.dumps(request))
    while not self.received_ack:
      time.sleep(0.1)
    self.pending_uuid = None

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
    if msg.topic.endswith("/from_device") and resp['kind'] == 'rpc_ok':
      print("received rpc_ok msg", resp['args'])
      if resp['args']['label'] == self.pending_uuid:
        print("MATCH for pending uuid")
        self.received_ack = True
    print("< _on_message")
