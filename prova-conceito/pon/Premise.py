from .Notifier import Notifier
from .Condition import Condition
from .NOPManager import NOPManager

import json


class Premise(Notifier):

    def __init__(self, at1, at2, cmp, id: int = 0):
        super().__init__(id)

        self.__at1 = at1
        self.__at2 = at2
        self.__cmp = cmp
        self.__elements = []

        self.__approved = self.approved()

        self.__at1.register(self)
        self.__at2.register(self)

    def update(self, id):

        approved = self.__cmp(
            self.__at1.value,
            self.__at2.value
        )

        if approved != self.__approved:

            self.__approved = approved

            for element in self.__elements:
                element.update(self.getId())

            if self.getId() != 0:
                NOPManager.GetInstance().update(
                    self.getId()
                )

    def register(self, notifiable):

        if notifiable not in self.__elements:
            self.__elements.append(notifiable)

    def approved(self):

        return self.__cmp(
            self.__at1.value,
            self.__at2.value
        )

    def getEncoded(self):

        return json.dumps({
            "v": 1 if self.approved() else 0
        })

    def handleEncoded(self, raw: str):

        try:

            print(
                "Premise::handleEncoded::warning: "
                "received data to local premise",
                raw
            )

        except Exception as e:

            print(
                "Premise::handleEncoded::error:",
                e
            )

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
    