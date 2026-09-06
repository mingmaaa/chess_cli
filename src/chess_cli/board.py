from position import Position

class Board:
    def __init__(self):
        self._grid = [[None for _ in range(8)] for _ in range(8)]

    def get(self,pos):
        return self._grid[pos.row][pos.col]

    def set(self,pos,piece):
        self._grid[pos.row][pos.col] = piece

    def is_empty(self,pos):
        return self.get(pos) is None

    def render(self):
        ...

        lines = []
        for row in range(7,-1,-1):
            row_cells = []
            for col in range(8):
                piece = self._grid[row][col]
                row_cells.append(str(piece) if piece else ".")
            lines.append(f"{row+1} " + " ".join(row_cells))
        lines.append("  "+ " ".join("abcdefgh"))
        return "\n".join(lines)