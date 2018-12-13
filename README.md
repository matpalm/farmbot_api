# a farmbot python api

a simple farmbot api focussed on image capture and annotation

## setup

comms with the farmbot is via [mqtt](http://mqtt.org/)

```
pip3 install paho-mqtt
```

use `request_token.py` to request an auth token for the farmbot api;
this script writes a `creds.py` file. do _NOT_ check creds.py in!!

`
./request_token.py --email YOUR_FARMBOT_EMAIL_LOGIN --password YOUR_PASSWORD
`

## use cases

demo use case of move to a position and take a photo

```
cat ./simple_move_eg.py

import creds
from client import FarmbotClient

client = FarmbotClient(creds.device_id, creds.token)
client.move(200, 700, 0)
client.take_photo()
client.shutdown()
```

everything is async so a captured image isn't immediately available during capture;
download all images after a sweep with `download_images` which uses the farmbot REST api

```
./download_images.py
```

run over
./sweep_bed.py




see https://gist.github.com/RickCarlino/10db2df375d717e9efdd3c2d9d8932af
for examples of rest api
