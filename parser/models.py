from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional


@dataclass
class Telemetry:
    timestamp: Optional[datetime] = None

    depth_m: Optional[float] = None
    temperature_c: Optional[float] = None
    absolute_pressure_pa: Optional[float] = None

    heart_rate_bpm: Optional[int] = None

    n2_load_percent: Optional[float] = None
    cns_load_percent: Optional[float] = None
    po2: Optional[float] = None
    time_to_surface_s: Optional[float] = None

    ascent_descent_rate_mps: Optional[float] = None

    def to_dict(self):
        data = asdict(self)

        if self.timestamp:
            data["timestamp"] = self.timestamp.isoformat()

        return data