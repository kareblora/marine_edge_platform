from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional


@dataclass
class Environment:
    depth_m: Optional[float] = None
    temperature_c: Optional[float] = None
    absolute_pressure_pa: Optional[float] = None


@dataclass
class Physiology:
    heart_rate_bpm: Optional[int] = None


@dataclass
class DiveState:
    n2_load_percent: Optional[float] = None
    cns_load_percent: Optional[float] = None
    po2: Optional[float] = None
    time_to_surface_s: Optional[float] = None


@dataclass
class Movement:
    ascent_descent_rate_mps: Optional[float] = None


@dataclass
class Telemetry:

    timestamp: Optional[datetime] = None

    device_id: str = "GARMIN-DIVE-001"
    diver_id: str = "DIVER-001"
    dive_id: str = "DIVE-136"

    environment: Optional[Environment] = None
    physiology: Optional[Physiology] = None
    dive: Optional[DiveState] = None
    movement: Optional[Movement] = None

    def to_dict(self):

        data = asdict(self)

        if self.timestamp:
            data["timestamp"] = self.timestamp.isoformat()

        return data

# @dataclass
# class Telemetry:
#     timestamp: Optional[datetime] = None

#     depth_m: Optional[float] = None
#     temperature_c: Optional[float] = None
#     absolute_pressure_pa: Optional[float] = None

#     heart_rate_bpm: Optional[int] = None

#     n2_load_percent: Optional[float] = None
#     cns_load_percent: Optional[float] = None
#     po2: Optional[float] = None
#     time_to_surface_s: Optional[float] = None

#     ascent_descent_rate_mps: Optional[float] = None

#     def to_dict(self):
#         data = asdict(self)

#         if self.timestamp:
#             data["timestamp"] = self.timestamp.isoformat()

#         return data