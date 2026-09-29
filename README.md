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