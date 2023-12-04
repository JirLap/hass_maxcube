from .device import MODE_NAMES, MaxDevice
from datetime import datetime

class MaxWallThermostat(MaxDevice):
    def __init__(self):
        super(MaxWallThermostat, self).__init__()
        self.comfort_temperature = None
        self.eco_temperature = None
        self.max_temperature = None
        self.min_temperature = None
        self.actual_temperature = None
        self.target_temperature = None
        self.mode = None

    def __str__(self):
        return self.describe(
            "WALLTHERMO",
            f"mode={MODE_NAMES.get(self.mode, str(self.mode))}",
            f"actual={self.actual_temperature}",
            f"target={self.target_temperature}",
            f"eco={self.eco_temperature}",
            f"comfort={self.comfort_temperature}",
            f"range=[{self.min_temperature},{self.max_temperature}]",
        )

    def get_programmed_temp_at(self, dt: datetime):
        """Retrieve the programmed temperature at the given instant."""
        weekday = PROG_DAYS[dt.weekday()]
        time = f"{dt.hour:02}:{dt.minute:02}"
        for point in self.programme.get(weekday, []):
            if time < point["until"]:
                return point["temp"]
        return None