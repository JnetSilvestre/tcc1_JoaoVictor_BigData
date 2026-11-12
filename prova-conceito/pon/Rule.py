from .Notifier import Notifier

import asyncio


class Rule(Notifier):

    def __init__(self, condition, action, id: int = 0):
        super().__init__(id)

        self.__condition = condition
        self.__action = action

        self.__condition.register(self)

    def update(self, id):

        if self.__condition.approved():

            try:
                asyncio.create_task(
                    self.execute()
                )

            except RuntimeError as e:
                print(
                    "Rule::update::error: "
                    "no running event loop:",
                    e
                )

    async def execute(self):

        self.__action.execute()