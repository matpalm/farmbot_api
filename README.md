# a farmbot python api

a simple farmbot api focussed on image capture and annotation

## setup

comms with the farmbot is via [mqtt](http://mqtt.org/)

```
pip3 install paho-mqtt
```

use `request_token.py` to request an auth token for the farmbot api; this script writes a `creds.py` file. do NOT check creds.py in!!

`
./request_token.py --email YOUR_FARMBOT_EMAIL_LOGIN --password YOUR_PASSWORD
`

./sweep_bed.py

./download_images.py


see https://gist.github.com/RickCarlino/10db2df375d717e9efdd3c2d9d8932af
for examples of rest api
