#!/usr/bin/env python3

import creds
from client import FarmbotClient

client = FarmbotClient(creds.device_id, creds.token)
client.move(0, 0, 0)
client.move(100, 100, 0)
client.shutdown()
