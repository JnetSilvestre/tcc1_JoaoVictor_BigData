class Action:
    def __init__(self, instigations):
        self.__instigations = instigations

    def execute(self):
        for ins in self.__instigations:
            ins.instigate()