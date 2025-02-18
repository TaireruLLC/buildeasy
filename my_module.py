from buildeasy import FileAsClass

class MyModule(FileAsClass):
    def __init__(self, name="buildeasy"):
        self.name = name

    def greet(self):
        return f"Hello from {self.name}!"