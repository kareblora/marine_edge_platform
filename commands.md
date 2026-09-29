# Installing required tools
sudo apt update
sudo apt install python3
sudo apt install python3.12-venv
sudo apt install git
sudo apt install sqlite3

# Setting up GIT credentials
git config --global user.email "kp.reblora@gmail.com"
git config --global user.name "kevin"

# Installing required python modules
python3 -m venv .venv
source .venv/bin/activate
pip install fitparse
pip install paho-mqtt

# Installing local MQTT broker
sudo apt install mosquitto mosquitto-clients
sudo systemctl enable --now mosquitto

# Checking MQTT client is sending messages
mosquitto_sub \
  -h localhost \
  -t 'marine/telemetry/GARMIN-DIVE-001/DIVE-136' \
  -v
