from statistics import mean

class DiveReport:

    def __init__(self, session, dive_summary, dive_settings,
                 dive_gas, events, telemetry):

        self.session = session
        self.dive_summary = dive_summary
        self.dive_settings = dive_settings
        self.dive_gas = dive_gas
        self.events = events
        self.telemetry = telemetry

    def _valid_values(self, field):
        values = []

        for record in self.telemetry:
            value = record.get(field)

            if value is not None:
                values.append(value)

        return values

    def get_environment_summary(self):

        temperatures = self._valid_values("temperature_c")
        pressures = self._valid_values("absolute_pressure_pa")
        depths = self._valid_values("depth_m")

        return {
            "temperature_min_c": min(temperatures) if temperatures else None,
            "temperature_max_c": max(temperatures) if temperatures else None,
            "pressure_min_pa": min(pressures) if pressures else None,
            "pressure_max_pa": max(pressures) if pressures else None,
            "depth_min_m": min(depths) if depths else None,
            "depth_max_m": max(depths) if depths else None,
        }

    def get_heart_rate_summary(self):

        values = self._valid_values("heart_rate_bpm")

        return {
            "average_bpm": round(mean(values), 1) if values else None,
            "min_bpm": min(values) if values else None,
            "max_bpm": max(values) if values else None,
        }


    def generate(self):

        environment = self.get_environment_summary()
        heart_rate = self.get_heart_rate_summary()

        summary = {}

    #    if self.dive_summary:
    #        summary = self.dive_summary[0]
        for item in self.dive_summary:
            if item.get("reference_mesg") == "session":
                summary = item
                break

    # Fall back to the first summary if no session reference exists.
        if not summary and self.dive_summary:
            summary = self.dive_summary[0]

        # Garmin FIT stores these two values in milliseconds.
        descent_time_ms = summary.get("unknown_15")
        ascent_time_ms = summary.get("unknown_16")

        descent_time_s = (
            descent_time_ms / 1000
            if descent_time_ms is not None
            else None
        )
        
        ascent_time_s = (
            ascent_time_ms / 1000
            if ascent_time_ms is not None
            else None
        )
        
        return {
            "telemetry_records": len(self.telemetry),
            "dive_number": summary.get("dive_number"),

            "average_depth_m": summary.get("avg_depth"),
            "maximum_depth_m": summary.get("max_depth"),
            "bottom_time_s": summary.get("bottom_time"),
            "descent_time_s": descent_time_s,
            "ascent_time_s": ascent_time_s,

            "environment": environment,

            "heart_rate": heart_rate,

            "events": len(self.events),

            "dive_settings": self.dive_settings,

            "dive_gas": self.dive_gas,
        }