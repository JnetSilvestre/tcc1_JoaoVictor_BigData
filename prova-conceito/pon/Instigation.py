class Instigation:

    def __init__(self, methods):
        self.__methods = methods

    def instigate(self):

        for method in self.__methods:
            method()