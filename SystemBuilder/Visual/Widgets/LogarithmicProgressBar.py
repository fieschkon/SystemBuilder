from enum import Enum
from PySide6.QtWidgets import QProgressBar
import math

class ProgressBiasType(Enum):
    FrontWeighted = 0
    BackWeighted = 1
    Linear = 2

class LogarithmicProgressBar(QProgressBar):
    def __init__(self, parent=None, mode : ProgressBiasType = ProgressBiasType.BackWeighted):
        self.biasmode = mode
        super().__init__(parent)

    def setValue(self, value):
        # Reverse logarithmic scaling to show longer increments towards the end
        super().setValue(self.getScaled(value))

    def getScaled(self, value):
        match self.biasmode:
            case ProgressBiasType.FrontWeighted:
                max_value = self.maximum()
                return max_value - (math.log10(max_value - value + 1) / math.log10(max_value + 1) * max_value)
            case ProgressBiasType.BackWeighted:
                max_value = self.maximum()
                return math.log10(value + 1) / math.log10(max_value + 1) * max_value
            case _:
                return value