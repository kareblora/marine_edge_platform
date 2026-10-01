#!/bin/bash

# Installing local Prometheus
sudo apt update
sudo apt install prometheus prometheus-node-exporter -y
sudo systemctl start prometheus

sudo apt-get install -y apt-transport-https wget gnupg

sudo mkdir -p /etc/apt/keyrings
sudo wget -O /etc/apt/keyrings/grafana.asc https://apt.grafana.com/gpg-full.key
sudo chmod 644 /etc/apt/keyrings/grafana.asc

echo "deb [signed-by=/etc/apt/keyrings/grafana.asc] https://apt.grafana.com stable main" \
  | sudo tee /etc/apt/sources.list.d/grafana.list

sudo apt update
sudo apt-get install grafana -y
sudo systemctl start grafana-server