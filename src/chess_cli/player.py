class Player:
    def __init__(self,name,color):
        self.name = name
        self.color = color
    def __repr__(self):
        return f"Player({self.name}), {self.color}"
    