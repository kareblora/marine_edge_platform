#!/bin/bash

kubectl create namespace monitoring

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm upgrade --install marine-monitoring \
  prometheus-community/kube-prometheus-stack \
  -n monitoring \
  -f k8s/monitoring/values.yaml

kubectl get secret \
  -n monitoring \
  marine-monitoring-grafana \
  -o jsonpath="{.data.admin-password}" | base64 -d


kubectl port-forward \
  --address 0.0.0.0 \
  -n monitoring \
  svc/marine-monitoring-grafana \
  3000:80

kubectl port-forward \
  --address 0.0.0.0 \
  -n monitoring \
  svc/marine-monitoring-kube-pro-prometheus \
  9090:9090