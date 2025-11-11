from enum import Enum


class RadiationDatabase(str, Enum):
    """Available radiation databases."""
    SARAH3 = "PVGIS-SARAH3"
    SARAH = "PVGIS-SARAH"
    NSRDB = "PVGIS-NSRDB"
    ERA5 = "PVGIS-ERA5"


class PVTechnology(str, Enum):
    """PV technology types."""
    CRYSTSI = "crystSi"
    CRYSTSI2025 = "crystSi2025"
    CIS = "CIS"
    CDTE = "CdTe"
    UNKNOWN = "Unknown"


class MountingPlace(str, Enum):
    """Mounting types for PV modules."""
    FREE = "free"
    BUILDING = "building"


class TrackingType(int, Enum):
    """Types of sun tracking systems."""
    FIXED = 0
    HORIZONTAL_NS = 1
    TWO_AXIS = 2
    VERTICAL = 3
    HORIZONTAL_EW = 4
    INCLINED_NS = 5


class OutputFormat(str, Enum):
    """Output format types."""
    JSON = "json"
    CSV = "csv"
    BASIC = "basic"
    EPW = "epw"
