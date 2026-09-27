from .models import (
    Telemetry,
    Environment,
    Physiology,
    DiveState,
    Movement
)


class MarineNormalizer:

    @staticmethod
    def normalize_record(record):

        return Telemetry(

            timestamp=record.get("timestamp"),

            environment=Environment(
                depth_m=record.get("depth"),
                temperature_c=record.get("temperature"),
                absolute_pressure_pa=record.get("absolute_pressure")
            ),

            physiology=Physiology(
                heart_rate_bpm=record.get("heart_rate")
            ),

            dive=DiveState(
                n2_load_percent=record.get("n2_load"),
                cns_load_percent=record.get("cns_load"),
                po2=record.get("po2"),
                time_to_surface_s=record.get("time_to_surface")
            ),

            movement=Movement(
                ascent_descent_rate_mps=record.get("ascent_descent_rate")
            )
        )

# from .models import Telemetry


# class MarineNormalizer:

#     @staticmethod
#     def normalize_record(record):

#         return Telemetry(
#             timestamp=record.get("timestamp"),

#             depth_m=record.get("depth"),
#             temperature_c=record.get("temperature"),
#             absolute_pressure_pa=record.get("absolute_pressure"),

#             heart_rate_bpm=record.get("heart_rate"),

#             n2_load_percent=record.get("n2_load"),
#             cns_load_percent=record.get("cns_load"),

#             po2=record.get("po2"),

#             time_to_surface_s=record.get("time_to_surface"),

#             ascent_descent_rate_mps=record.get(
#                 "ascent_descent_rate"
#             )
#         )