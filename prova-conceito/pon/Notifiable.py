class Notifiable:

    def __init__(self):
        pass

    def update(self, id):
        raise NotImplementedError(
            "Classes derivadas devem implementar o método update()."
        )