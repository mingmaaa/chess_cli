class Position:
    def __init__(self,row,col):
        self.row = row
        self.col = col
    def __eq__(self,other):
        if not isinstance(other,Position):
            return NotImplemented
        return self.row == other.row and self.col == other.col

    def __hash__(self):
        return hash((self.row,self.col))

    def __repr__(self):
        return f"Position({self.row},{self.col})"

    @classmethod 
    def from_algebraic(cls,s):
        col = ord(s[0]) - ord('a')
        row = int((s[1]-1))
        return cls(row,col)

