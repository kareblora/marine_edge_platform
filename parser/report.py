from statistics import mean


class DiveReport:

    def __init__(
        self,
        session,
        dive_summary,
        dive_settings,
        dive_gas,
        events,
        telemetry
    ):
        self.session = session
        self.dive_summary = dive_summary
        self.dive_settings = dive_settings
        self.dive_gas = dive_gas
        self.events = events
        self.telemetry = telemetry

    def _valid_values(self, section, field):
        """
        Get valid values from nested telemetry data.

        Example:
            environment -> depth_m
            physiology -> heart_rate_bpm
        """

        values = []

        for record in self.telemetry:

            section_data = record.get(section, {})

            if section_data is None:
                continue

            value = section_data.get(field)

            if value is not None:
                values.append(value)

        return values

    def _get_session_summary(self):

        for summary in self.dive_summary:

            if summary.get("reference_mesg") == "session":
                return summary

        if self.dive_summary:
            return self.dive_summary[0]

        return {}

    def get_environment_summary(self):

        temperatures = self._valid_values(
            "environment",
            "temperature_c"
        )

        pressures = self._valid_values(
            "environment",
            "absolute_pressure_pa"
        )

        depths = self._valid_values(
            "environment",
            "depth_m"
        )

        return {
            "temperature_min_c":
                min(temperatures) if temperatures else None,

            "temperature_max_c":
                max(temperatures) if temperatures else None,

            "pressure_min_pa":
                min(pressures) if pressures else None,

            "pressure_max_pa":
                max(pressures) if pressures else None,

            "depth_min_m":
                min(depths) if depths else None,

            "depth_max_m":
                max(depths) if depths else None,
        }

    def get_heart_rate_summary(self):

        values = self._valid_values(
            "physiology",
            "heart_rate_bpm"
        )

        return {
            "average_bpm":
                round(mean(values), 1) if values else None,

            "min_bpm":
                min(values) if values else None,

            "max_bpm":
                max(values) if values else None,
        }

    def generate(self):

        summary = self._get_session_summary()

        environment = self.get_environment_summary()

        heart_rate = self.get_heart_rate_summary()

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

        bottom_time_s = summary.get("bottom_time")

        surface_interval_s = summary.get("surface_interval")

        return {

            "telemetry_records": len(self.telemetry),

            "dive_number":
                summary.get("dive_number"),

            "timestamp":
                summary.get("timestamp"),

            "average_depth_m":
                summary.get("avg_depth"),

            "maximum_depth_m":
                summary.get("max_depth"),

            "bottom_time_s":
                bottom_time_s,

            "descent_time_s":
                descent_time_s,

            "ascent_time_s":
                ascent_time_s,

            "surface_interval_s":
                surface_interval_s,

            "start_n2_percent":
                summary.get("start_n2"),

            "end_n2_percent":
                summary.get("end_n2"),

            "start_cns_percent":
                summary.get("start_cns"),

            "end_cns_percent":
                summary.get("end_cns"),

            "environment":
                environment,

            "heart_rate":
                heart_rate,

            "events":
                len(self.events),

            "dive_settings":
                self.dive_settings,

            "dive_gas":
                self.dive_gas,
        }