# mosquitto-mqtt-oauth

https://mosquitto.org/

https://pypi.org/project/mosmqtt-oauth/

## Prerequisites

 - Ubuntu System
 - Python 3

## Usage
```
pip install mosmqtt_oauth

sudo apt-add-repository ppa:mosquitto-dev/mosquitto-ppa

sudo apt-get update

sudo apt-get install mosquitto=2.0.8-0mosquitto1~focal1

cp auth_plugin_pyauth.so  /usr/local/lib/auth_plugin_pyauth.so 

cp mosmqtt_oauth.conf /etc/mosquitto/conf.d/ 

cp mosmqtt_oauth.env /etc/mosquitto/

```

## Setting environment variable
Try if environment variables can be set to system via systemd

```
grep -q "EnvironmentFile" /lib/systemd/system/mosquitto.service || sed -i 's/\[Service\]/\[Service\]\nEnvironmentFile\=\/etc\/mosquitto\/mosmqtt_oauth.env/' /lib/systemd/system/mosquitto.service

systemctl daemon-reload
```

