                     Marine Edge Platform

Sensors ──► MQTT ──► Telemetry Service
                       │
                       ▼
                 Normalization
                       │
              ┌────────┴────────┐
              ▼                 ▼
           Storage         Observability
              │                 │
              ▼                 ▼
          PostgreSQL         Grafana
              │
              ▼
          Cloud Sync




                         K3s EDGE CLUSTER
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  namespace: marine-edge                                    │
│                                                             │
│  ┌──────────────┐                                           │
│  │  Publisher   │                                           │
│  │     Job      │                                           │
│  └──────┬───────┘                                           │
│         │ MQTT                                              │
│         ▼                                                   │
│  ┌──────────────┐       ┌─────────────────────────────┐     │
│  │  Mosquitto   │──────▶│      Subscriber             │     │
│  │ Deployment   │       │ Deployment                  │     │
│  │ + Service    │       │ + Service                   │     │
│  └──────────────┘       │ + Readiness endpoint        │     │
│                         │ + SQLite PVC                 │     │
│                         └─────────────┬───────────────┘     │
│                                       │                     │
│                                       │ readiness           │
│                                       ▼                     │
│                         ┌─────────────────────────────┐     │
│                         │       Sync Agent            │     │
│                         │       Deployment             │     │
│                         │       + publisher PVC        │     │
│                         └─────────────────────────────┘     │
│                                                             │
│             ConfigMap + Persistent Volumes                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘