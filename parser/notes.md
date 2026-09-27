             Garmin FIT file
                    │
                    ▼
            ┌───────────────┐
            │  FIT Parser   │
            └───────┬───────┘
                    │
                    ▼
             Raw FIT records
                    │
                    ▼
            ┌───────────────┐
            │  Normalizer   │
            └───────┬───────┘
                    │
                    ▼
           Marine Telemetry
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
   JSON data file        Dive Report


main.py (orchestrator)
   │
   ├── read FIT file
   ├── call parser
   ├── call normalizer
   ├── generate report
   └── save JSON

fit_parser.py --> Read the Garmin FIT file and extract the data

models.py --> Define our marine telementry data model (standard schema)
          --> Telemetry class convert Python object into a dictionary
          --> Dictionaries can easily be converted into JSON

normalizer.py --> convert Garmin-specific raw data into our satandard marine telemetry model

report.py --> take normalized telemetry and dive metadata and turn it into useful information

                 Garmin FIT
                     │
                     ▼
              ┌─────────────┐
              │ FIT Parser  │
              │    (RAW)    │
              │ Ingestion   │
              └──────┬──────┘
                     │
                     ▼
              ┌─────────────┐
              │ Normalizer  │
              │             │
              │ Translation │
              └──────┬──────┘
                     │
                     ▼
              ┌─────────────┐
              │  Telemetry  │
              │    Model    │
              │             │
              │ Data Model  │
              └──────┬──────┘
                     │---------------> marine_telemetry,json
                     ▼
              ┌─────────────┐
              │ Dive Report │
              │             │
              │ Presentation│
              └─────────────┘
 