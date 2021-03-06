# a farmbot python api

a simple farmbot api focussed on bulk image capture and annotation

![images_eg.gif](images_eg.gif)

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

a common use case is the combo of sweeping across the bed capturing images,
downloading them all and then run detections

```
./sweep_bed.py
./download_images.py
./calculate_detections.py
```

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

### show all images for a specific coord

show a collage with all images for a specific (x, y, z). assumes z=0 if only two args provided.

```
./show_images_for.py 200 200
```

### annotate images without detections

run faster rcnn on all images that haven't been run yet.
we calculate detections for the image as captured as well as rotated by 90, 180 and 270 degrees.

```
./calculate_detections.py
```

### show annotations for a specific image

```
./show_detections.py imgs/20181122/140032.jpg
```

### tail all logs from farmbot

```
./tail_logs.py
```