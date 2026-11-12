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
        # 0 representa entidade apenas local, sem registro no manager.
        if isinstance(id, bool) or not isinstance(id, int) or id < 0:
            raise ValueError("Notifier::setId: id must be a non-negative integer")

        if id == self.__id:
            return

        manager = NOPManager.GetInstance()

        # Validar ANTES de remover o registro anterior para preservar
        # a entidade caso o novo ID esteja ocupado.
        if id != 0:
            existing = manager.entities.get(id)
            if existing is not None and existing is not self:
                raise ValueError(f"Notifier::setId: id {id} already registered")

        if self.__id != 0:
            manager.removeEntity(self)

        self.__id = id
        if id != 0:
            manager.addEntity(self)

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
