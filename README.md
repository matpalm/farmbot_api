# a farmbot python api

a simple farmbot api focussed on bulk image capture and annotation

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

### simple move

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

### sweep entire bed

use sweep bed to sweep over entire farm bed taking images

```
./sweep_bed.py --min-x 0 --max-x 2500 --min-y 0 --max-y 1300 --delta 500 --dry-run
15 [(0, 0), (0, 500), (0, 1000), (500, 1000), (500, 500), (500, 0), (1000, 0), (1000, 500), (1000, 1000), (1500, 1000), (1500, 500), (1500, 0), (2000, 0), (2000, 500), (2000, 1000)]
```

### download all images

everything is async so a requested image might be captured by isn't immediately available for download.
so when doing sweep captures we download images in bulk.
uses the [farmbot REST api](https://gist.github.com/RickCarlino/10db2df375d717e9efdd3c2d9d8932af) to download
all images and then delete them from cloud storage.

```
./download_images.py
```

### annotate images

WIP


### tail all logs from farmbot

```
./tail_logs.py
```