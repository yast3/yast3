from ...module import Module


class PackagesModule(Module):
    def __init__(self):
        super().__init__("Packages", ("package-manager", "package"))