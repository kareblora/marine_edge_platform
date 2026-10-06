import uuid
import logging

from .models import (
    Telemetry,
    Environment,
    Physiology,
    DiveState,
    Movement,
    TelemetryQuality
)

logger = logging.getLogger("MarineNormalizer")

class MarineNormalizer:

    @staticmethod
    def normalize_record(record, device_id, diver_id, dive_id):

        try:
            message_id = str(uuid.uuid4())
            environment = Environment(
                depth_m=record.get("depth"),
                temperature_c=record.get("temperature"),
                absolute_pressure_pa=record.get("absolute_pressure")
            )

            physiology = Physiology(
                heart_rate_bpm=record.get("heart_rate")
            )

            dive = DiveState(
                n2_load_percent=record.get("n2_load"),
                cns_load_percent=record.get("cns_load"),
                po2=record.get("po2"),
                time_to_surface_s=record.get("time_to_surface")
            )

            movement = Movement(
                ascent_descent_rate_mps=record.get("ascent_descent_rate")
            )

            quality = MarineNormalizer.calculate_quality(
                environment,
                physiology,
                dive,
                movement
            )

            return Telemetry(
                message_id=message_id,
                timestamp=record.get("timestamp"),
                
                device_id=device_id,
                diver_id=diver_id,
                dive_id=dive_id,

                environment=environment,
                physiology=physiology,
                dive=dive,
                movement=movement,

                quality=quality
            )
            
        except Exception as error:
            logger.error(
                "Failed to normalize telemetry record at timestamp %s: %s",
                record.get("timestamp"),
                error
            )
            raise

    @staticmethod
    def calculate_quality(
        environment,
        physiology,
        dive,
        movement
    ):

        fields = {
            "environment.depth_m": environment.depth_m,
            "environment.temperature_c": environment.temperature_c,
            "environment.absolute_pressure_pa":
                environment.absolute_pressure_pa,

            "physiology.heart_rate_bpm":
                physiology.heart_rate_bpm,

            "dive.n2_load_percent":
                dive.n2_load_percent,

            "dive.cns_load_percent":
                dive.cns_load_percent,

            "dive.po2":
                dive.po2,

            "dive.time_to_surface_s":
                dive.time_to_surface_s,

            "movement.ascent_descent_rate_mps":
                movement.ascent_descent_rate_mps
        }

        total_fields = len(fields)

        missing_fields = [
            name
            for name, value in fields.items()
            if value is None
        ]

        available_fields = total_fields - len(missing_fields)

        completeness = (
            available_fields / total_fields
        ) * 100

        completeness = round(completeness, 1)

        if completeness == 100:
            status = "COMPLETE"

        elif completeness >= 75:
            status = "PARTIAL"

        else:
            status = "DEGRADED"

        return TelemetryQuality(
            status=status,
            completeness_percent=completeness,
            missing_fields=missing_fields
        )

