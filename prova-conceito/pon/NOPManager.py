from .Notifiable import Notifiable

import asyncio


class NOPManager(Notifiable):

    __Instance = None

    def __init__(self):
        self.__drivers = []
        self.__tasks_entries = []
        self.__entities = {}

    async def run(self, forever: bool = True):
        for task in self.__tasks_entries:
            asyncio.create_task(task.task_entry())

        for driver in self.__drivers:
            asyncio.create_task(driver.run())

        while forever:
            await asyncio.sleep(0.001)

    def addTask(self, entry):
        self.__tasks_entries.append(entry)

    @property
    def entities(self):
        return self.__entities

    def addEntity(self, notifier):
        if notifier.getId() == 0:
            raise ValueError(
                "NOPManager::addEntity: Invalid entity with id 0"
            )

        self.__entities[notifier.getId()] = notifier

    def removeEntity(self, notifier):
        entity_id = notifier.getId()

        if entity_id in self.__entities:
            del self.__entities[entity_id]

    def addDriver(self, driver):
        self.__drivers.append(driver)

    def removeDriver(self, driver):
        if driver in self.__drivers:
            self.__drivers.remove(driver)

    def update(self, id: int):
        if id == 0:
            return

        entity = self.__entities.get(id)

        if entity is not None:
            self.sendNotificationToDriver(entity)

    def sendNotificationToDriver(self, entity):
        encoded = entity.getEncoded()
        entity_id = entity.getId()

        for driver in self.__drivers:
            driver.sendNotification(entity_id, encoded)

    def handleDriverNotification(self, id, data):
        entity = self.__entities.get(id)

        if entity is not None:
            entity.handleEncoded(data)

    @staticmethod
    def GetInstance():
        if NOPManager.__Instance is None:
            NOPManager.__Instance = NOPManager()

        return NOPManager.__Instance