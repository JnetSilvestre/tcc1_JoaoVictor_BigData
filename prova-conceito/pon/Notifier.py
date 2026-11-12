from .Notifiable import Notifiable
from .NOPManager import NOPManager


class Notifier(Notifiable):

    def __init__(self, id: int = 0):
        super().__init__()

        self.__id = 0
        self.__elements = []

        if id != 0:
            self.setId(id)

    def getId(self):
        return self.__id

    def setId(self, id: int):

        if self.__id != 0 and self.__id != id:
            NOPManager.GetInstance().removeEntity(self)

        self.__id = id

        if self.__id != 0:
            NOPManager.GetInstance().addEntity(self)

    def update(self, id):

        for element in self.__elements:
            element.update(self.__id)

        if self.__id != 0:
            NOPManager.GetInstance().update(self.__id)

    def notify(self):

        for element in self.__elements:
            element.update(self.__id)

    def register(self, notifiable):

        if notifiable not in self.__elements:
            self.__elements.append(notifiable)

    def getEncoded(self):
        raise NotImplementedError(
            "Classes derivadas devem implementar getEncoded()."
        )

    def handleEncoded(self, data):
        raise NotImplementedError(
            "Classes derivadas devem implementar handleEncoded()."
        )