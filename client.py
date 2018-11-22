import paho.mqtt.client as mqtt
import json
import time
from uuid import uuid4
import logging

# values over max (and under min) will be clipped
MAX_X = 2400
MAX_Y = 1200
MIN_Z = -400  # TODO test this one!

def coord(x, y, z):
  return {"kind": "coordinate", "args": {"x": x, "y": y, "z": z}}

def move_request(x, y, z):
  return {"kind": "rpc_request",
          "args": {"label": ""},
          "body": [{"kind": "move_absolute",
                    "args": {"location": coord(x, y, z),
                             "offset": coord(0, 0, 0),
                             "speed": 100}}]}

def take_photo_request():
  return {"kind": "rpc_request",
          "args": {"label": ""},
          "body": [{"kind": "take_photo", "args": {}}]}

def clip(v, min_v, max_v):
  if v < min_v: return min_v
  if v > max_v: return max_v
  return v

class FarmbotClient(object):

  def __init__(self, device_id, token):

    self.device_id = device_id
    self.client = mqtt.Client()
    self.client.username_pw_set(self.device_id, token)
    self.client.on_connect = self._on_connect
    self.client.on_message = self._on_message

    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s",
                        filename='farmbot_client.log',
                        filemode='a')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter("%(asctime)s\t%(message)s"))
    logging.getLogger('').addHandler(console)

    self.connected = False
    self.client.connect("brisk-bear.rmq.cloudamqp.com", 1883, 60)
    self.client.loop_start()


  def shutdown(self):
    self.client.disconnect()
    self.client.loop_stop()

  def move(self, x, y, z):
    x = clip(x, 0, MAX_X)
    y = clip(y, 0, MAX_Y)
    z = clip(z, MIN_Z, 0)
    status_ok = self._blocking_request(move_request(x, y, z))
    logging.info("MOVE (%s,%s,%s) [%s]", x, y, z, status_ok)

  def take_photo(self):
    # TODO: is this enough? it's issue a request for the photo, but is the actual capture async?
    status_ok = self._blocking_request(take_photo_request())
    logging.info("TAKE_PHOTO [%s]", status_ok)

  def _blocking_request(self, request, retries_remaining=3):

    if retries_remaining==0:
      logging.error("< blocking request [%s] OUT OF RETRIES", request)
      return False

    self._wait_for_connection()

    # assign a new uuid for this attempt
    self.pending_uuid = str(uuid4())
    request['args']['label'] = self.pending_uuid
    logging.debug("> blocking request [%s] retries=%d", request, retries_remaining)

    # send request off
    self.rpc_status = None
    self.client.publish("bot/" + self.device_id + "/from_clients", json.dumps(request))

    # wait for response
    timeout_counter = 600  # ~1min
    while self.rpc_status is None:
      time.sleep(0.1)
      timeout_counter -= 1
      if timeout_counter == 0:
        logging.warn("< blocking request TIMEOUT [%s]", request)
        return self._blocking_request(request, retries_remaining-1)
    self.pending_uuid = None

    # if it's ok, we're done!
    if self.rpc_status == 'rpc_ok':
      logging.debug("< blocking request OK [%s]", request)
      return True

    # if it's not ok, wait a bit and retry
    if self.rpc_status == 'rpc_error':
      logging.warn("< blocking request ERROR [%s]", request)
      time.sleep(1)
      return self._blocking_request(request, retries_remaining-1)

    # unexpected state (???)
    msg = "unexpected rpc_status [%s]" % self.rpc_status
    logging.error(msg)
    raise Exception(msg)


  def _wait_for_connection(self):
    # TODO: better way to do all this async event driven rather than with polling :/
    timeout_counter = 600  # ~1min
    while not self.connected:
      time.sleep(0.1)
      timeout_counter -= 1
      if timeout_counter == 0:
        raise Exception("unable to connect")

  def _on_connect(self, client, userdata, flags, rc):
    logging.debug("> _on_connect")
    self.client.subscribe("bot/" + self.device_id + "/from_device")
    self.connected = True
    logging.debug("< _on_connect")

  def _on_message(self, client, userdata, msg):
    resp = json.loads(msg.payload)
    if resp['args']['label'] != 'ping':
      logging.debug("> _on_message [%s] [%s]", msg.topic, resp)
    if msg.topic.endswith("/from_device") and resp['args']['label'] == self.pending_uuid:
      self.rpc_status = resp['kind']
