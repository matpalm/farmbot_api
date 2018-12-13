#!/usr/bin/env python3
import creds
from client import FarmbotClient

client = FarmbotClient(creds.device_id, creds.token)
client.move(200, 700, 0)
client.take_photo()
client.shutdown()
