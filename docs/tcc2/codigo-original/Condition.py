from .Notifier import Notifier
from .NOPManager import NOPManager

import json


class Condition(Notifier):

    def __init__(self, operation, elements, id: int = 0):
        super().__init__(id)

        self.__operation = operation
        self.__elements = elements
        self.__approved = self.approved()

        for element in self.__elements:
            element.register(self)

    def update(self, id):

        approved = self.__operation()

        if approved != self.__approved:

            self.__approved = approved

            for element in self.__elements:
                element.update(self.__id)

            if self.__id != 0:
                NOPManager.GetInstance().update(self.__id)

    def getEncoded(self):

        return json.dumps({
            "v": 1 if self.__operation() else 0
        })

    def handleEncoded(self, raw: str):

        try:

            print(
                "Condition::handleEncoded::warning: "
                "received data to local condition",
                raw
            )

        except Exception as e:

            print(
                "Condition::handleEncoded::error:",
                e
            )

    def approved(self):

        return self.__operation()

    def __and__(self, other):

        return Condition(
            lambda: self.approved() and other.approved(),
            [self, other]
        )

    def __or__(self, other):

        return Condition(
            lambda: self.approved() or other.approved(),
            [self, other]
        )