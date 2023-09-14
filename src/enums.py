from enum import Enum


class Func(Enum):
    pretty = 'pretty'
    file = 'file'

    def __str__(self):
        return self.name

    @staticmethod
    def from_string(s):
        try:
            return Func[s]
        except KeyError:
            raise ValueError()
