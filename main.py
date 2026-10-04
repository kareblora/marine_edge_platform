import json
import sys
from pathlib import Path

from parser.fit_parser import GarminFitParser
from parser.normalizer import MarineNormalizer
from parser.report import DiveReport
from parser.config import MarineConfig
from parser.outbox import TelemetryOutbox

def format_minutes(seconds):
    
    if seconds is None:
        return "N/A"

    minutes = seconds / 60

    return f"{minutes:.2f} min"


def format_timestamp(timestamp):

    if timestamp is None:
        return "N/A"

    return str(timestamp)

def main():

    if len(sys.argv) != 2:
        print("Usage:")
        print("  python main.py <fit-file>")
        sys.exit(1)

    fit_file = Path(sys.argv[1])
    
    config = MarineConfig("config/config.json")

    device_id = config.get("device_id")
    diver_id = config.get("diver_id")
    dive_id = config.get("dive_id")
      
    database_path = config.get_publisher_database()
    
    outbox = TelemetryOutbox(database_path)
        
    mqtt_config = config.get_mqtt_config()
    
    if not fit_file.exists():
        print(f"File not found: {fit_file}")
        sys.exit(1)

    print(f"Reading: {fit_file}")

    parser = GarminFitParser(fit_file)

    records = parser.get_records()
    session = parser.get_session()
    dive_summary = parser.get_dive_summary()     
    dive_settings = parser.get_dive_settings()
    dive_gas = parser.get_dive_gas()
    events = parser.get_events()

    normalized_data = [
        MarineNormalizer.normalize_record(
            record,
            device_id,
            diver_id,
            dive_id
        ).to_dict()
        for record in records
    ]
    
    topic = (
        f"{mqtt_config['topic_prefix']}/"
        f"{device_id}/"
        f"{dive_id}"
    )

    print("Staging telemetry in durable outbox...")

    for telemetry in normalized_data:

        message_id = telemetry["message_id"]

        outbox.add(
            message_id,
            topic,
            telemetry
        )

    print(
        f"Telemetry staged in outbox: "
        f"{len(normalized_data):,} messages"
    )

# ---------------------------------------------------------
# DIVE OPERATIONAL REPORT -- SOURCE
# ---------------------------------------------------------

    print()
    print("=" * 64)
    print("              MARINE EDGE - DIVE OPERATIONAL REPORT")
    print("=" * 64)

    print()

    print("SOURCE")
    print("-" * 64)

    print(f"File                : {fit_file.name}")

    report_generator = DiveReport(
        session=session,
        dive_summary=dive_summary,
        dive_settings=dive_settings,
        dive_gas=dive_gas,
        events=events,
        telemetry=normalized_data
    )

    report = report_generator.generate()

# ---------------------------------------------------------
# DIVE OPERATIONAL REPORT
# ---------------------------------------------------------

    print(f"Telemetry Records   : {report['telemetry_records']:,}")
    print(f"Dive Number         : {report['dive_number']}")
    print(f"Dive Timestamp      : {format_timestamp(report['timestamp'])}")

    print()

    print("DIVE PROFILE")
    print("-" * 64)

    print(
        f"Average Depth       : "
        f"{report['average_depth_m']:.2f} m"
    )

    print(
        f"Maximum Depth       : "
        f"{report['maximum_depth_m']:.2f} m"
    )

    print(
        f"Bottom Time         : "
        f"{format_minutes(report['bottom_time_s'])}"
    )

    print(
        f"Descent Time        : "
        f"{format_minutes(report['descent_time_s'])}"
    )

    print(
        f"Ascent Time         : "
        f"{format_minutes(report['ascent_time_s'])}"
    )

    print(
        f"Surface Interval    : "
        f"{format_minutes(report['surface_interval_s'])}"
    )

    print()

    print("ENVIRONMENT")
    print("-" * 64)

    environment = report["environment"]

    print(
        f"Depth Range         : "
        f"{environment['depth_min_m']} - "
        f"{environment['depth_max_m']} m"
    )

    print(
        f"Temperature         : "
        f"{environment['temperature_min_c']} - "
        f"{environment['temperature_max_c']} °C"
    )

    print(
        f"Pressure Range      : "
        f"{environment['pressure_min_pa']} - "
        f"{environment['pressure_max_pa']} Pa"
    )

    print()

    print("DIVER PHYSIOLOGY")
    print("-" * 64)

    heart_rate = report["heart_rate"]

    print(
        f"Heart Rate Average  : "
        f"{heart_rate['average_bpm']} bpm"
    )

    print(
        f"Heart Rate Minimum  : "
        f"{heart_rate['min_bpm']} bpm"
    )

    print(
        f"Heart Rate Maximum  : "
        f"{heart_rate['max_bpm']} bpm"
    )

    print()

    print("DIVE GAS")
    print("-" * 64)

    if report["dive_gas"]:

        gas = report["dive_gas"][0]

        print(
            f"Oxygen              : "
            f"{gas.get('oxygen_content', 'N/A')} %"
        )

        print(
            f"Helium              : "
            f"{gas.get('helium_content', 'N/A')} %"
        )

    else:

        print("Gas information     : N/A")

    print()

    print("DIVE STATE")
    print("-" * 64)

    print(
        f"Starting N2 Load    : "
        f"{report['start_n2_percent']} %"
    )

    print(
        f"Ending N2 Load      : "
        f"{report['end_n2_percent']} %"
    )

    print(
        f"Starting CNS        : "
        f"{report['start_cns_percent']} %"
    )

    print(
        f"Ending CNS          : "
        f"{report['end_cns_percent']} %"
    )

    print()

    print("EVENTS")
    print("-" * 64)

    print(
        f"Total Events        : "
        f"{report['events']}"
    )

    print()

    print("PLATFORM INGESTION")
    print("-" * 64)

    print("Source Format       : Garmin FIT")

    print(
        f"Records Processed   : "
        f"{report['telemetry_records']:,}"
    )

    print("Telemetry Status    : OK")

    print()

    print("=" * 64)

    output = {
    "schema_version": "1.0",

    "source": {
        "format": "garmin_fit",
        "file": str(fit_file),
        "device_id": device_id,
        "parser": "MarineEdge Garmin FIT Parser"
    },

    "telemetry": normalized_data
}


    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "marine_telemetry.json"

    with open(output_file, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print()
    print(f"Normalized output: {output_file}")


if __name__ == "__main__":
    main()
