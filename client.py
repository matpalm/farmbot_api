import paho.mqtt.client as mqtt
import json
import time
from uuid import uuid4

def coord(x, y, z):
  return {"kind": "coordinate", "args": {"x": x, "y": y, "z": z}}

def move_request(x, y, z):
  return {"kind": "rpc_request",
          "args": {"label": ""},
          "body": [{"kind": "move_absolute",
                    "args": {"location": coord(x, y, z),
                             "offset": coord(0, 0, 0),
                             "speed": 50}}]}

def take_photo_request():
  return {"kind": "rpc_request",
          "args": {"label": ""},
          "body": [{"kind": "take_photo", "args": {}}]}

def clip(x, min_v, max_v):
  if x < min_v: return min_v
  if x > max_v: return max_v
  return x

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
    x = clip(x, 0, 2400)
    y = clip(y, 0, 1200)
    start = time.time()
    print("> move", x, y, z)
    status_ok = self._blocking_request(move_request(x, y, z))
    print("< move", status_ok, time.time()-start)

  def take_photo(self):
    # TODO: is this enough? it's issue a request for the photo, but is the actual capture async?
    start = time.time()
    print("> take photo")
    status_ok = self._blocking_request(take_photo_request())
    print("< take photo", status_ok, time.time()-start)

  def _blocking_request(self, request, retries_remaining=3):
    print("> blocking request", request, "retries_remaining", retries_remaining)
    self._wait_for_connection()

    # assign a new uuid for this attempt
    self.pending_uuid = str(uuid4())
    request['args']['label'] = self.pending_uuid

    # send request off
    self.rpc_status = None
    self.client.publish("bot/" + self.device_id + "/from_clients", json.dumps(request))

    # wait for response
    timeout_counter = 600  # 1min
    while self.rpc_status is None:
      time.sleep(0.1)
      timeout_counter -= 1
      if timeout_counter % 10 == 0:
        print("waiting....", timeout_counter)
      if timeout_counter == 0:
        print("timeout...", self.pending_uuid)
        return self._blocking_request(request, retries_remaining-1)
    self.pending_uuid = None

    # if it's ok, we're done!
    if self.rpc_status == 'rpc_ok':
      return True

    # if it's not ok, wait a bit and either retry or give up
    if self.rpc_status == 'rpc_error':
      print("rpc_failed! :/")
      time.sleep(1)
      if retries_remaining > 0:
        return self._blocking_request(request, retries_remaining-1)
      return False

    # unexpected state
    # TODO: should record entire message here i guess...
    raise Exception("unexpected rpc_status [%s]" % self.rpc_status)


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
    resp = json.loads(msg.payload)
    if msg.topic.endswith("/from_device") and resp['args']['label'] == self.pending_uuid:
      print("received msg", resp)
      self.rpc_status = resp['kind']
