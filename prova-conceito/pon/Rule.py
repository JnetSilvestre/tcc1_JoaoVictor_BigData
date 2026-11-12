from .Notifier import Notifier


class Rule(Notifier):
    """Regra local ativada por transições da condição associada.

    O caminho normal da cadeia PON é síncrono: Condition.update() notifica
    Rule.update(), que executa a Action antes de retornar. Isso torna o
    oráculo C0 determinístico e não depende de um event loop ativo.

    execute() permanece awaitable para compatibilidade com o código-base;
    chamá-lo diretamente executa a ação de forma explícita.
    """

    def __init__(self, condition, action, id: int = 0):
        super().__init__(id)
        self.__condition = condition
        self.__action = action
        self.__condition.register(self)

    def update(self, id):
        # Condition somente notifica observadores quando muda de estado.
        # Transições para falso não disparam a ação.
        if self.__condition.approved():
            self._execute_action()

    def _execute_action(self):
        self.__action.execute()

    async def execute(self):
        self._execute_action()
