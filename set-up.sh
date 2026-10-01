#!/bin/bash

# Setting up GIT credentials
sudo apt install git -y
git config --global user.email "kp.reblora@gmail.com"
git config --global user.name "kevin"
git clone https://github.com/kareblora/marine_edge_platform.git
cd marine_edge_platform
git checkout observability

# Installing required tools
sudo apt update -y
sudo apt install python3 -y
sudo apt install python3.12-venv -y
sudo apt install sqlite3 -y

# Installing required python modules
python3 -m venv .venv
source .venv/bin/activate
pip install fitparse
pip install paho-mqtt
pip install prometheus-client

# Installing local MQTT broker
sudo apt install mosquitto mosquitto-clients -y
sudo systemctl enable --now mosquitto

# Checking MQTT client is sending messages
#mosquitto_sub \
#  -h localhost \
#  -t 'marine/telemetry/GARMIN-DIVE-001/DIVE-136' \
#  -v

# Checking SQL database
# sqlite3 output/publisher.db \
# "SELECT COUNT(*) FROM outbox WHERE status='PENDING';"