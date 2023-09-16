from enum import Enum


class OutputVariant(Enum):
    pretty = 'pretty'
    file = 'file'

    def __str__(self):
        return self.name

    @staticmethod
    def from_string(s):
        try:
            return OutputVariant[s]
        except KeyError:
            raise ValueError()
