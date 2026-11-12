from .Notifier import Notifier
from .Premise import Premise

import json


class Attribute(Notifier):

    def __init__(self, value, id: int = 0):
        super().__init__(id)
        self.__value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):

        if self.__value != value:
            self.__value = value
            self.update(self.getId())

    def set_value(self, value):

        if self.__value != value:
            self.__value = value
            self.update(self.getId())

    def getEncoded(self):

        return json.dumps({
            "v": self.value
        })

    def handleEncoded(self, raw: str):

        try:
            data = json.loads(raw)

            value = data.get("v")

            if value is not None and self.__value != value:
                self.set_value(value)

        except (json.JSONDecodeError, TypeError) as e:

            print(
                "Attribute::handleEncoded::error:",
                e
            )

    def __gt__(self, value):

        if not isinstance(value, Attribute):
            value = Attribute(value)

        return Premise(
            self,
            value,
            lambda a, b: a > b
        )

    def __ge__(self, value):

        if not isinstance(value, Attribute):
            value = Attribute(value)

        return Premise(
            self,
            value,
            lambda a, b: a >= b
        )

    def __lt__(self, value):

        if not isinstance(value, Attribute):
            value = Attribute(value)

        return Premise(
            self,
            value,
            lambda a, b: a < b
        )

    def __le__(self, value):

        if not isinstance(value, Attribute):
            value = Attribute(value)

        return Premise(
            self,
            value,
            lambda a, b: a <= b
        )

    def __ne__(self, value):

        if not isinstance(value, Attribute):
            value = Attribute(value)

        return Premise(
            self,
            value,
            lambda a, b: a != b
        )

    def __eq__(self, value):

        if not isinstance(value, Attribute):
            value = Attribute(value)

        return Premise(
            self,
            value,
            lambda a, b: a == b
        )