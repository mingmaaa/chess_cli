from position import Position
from piece import Pawn, Knight, Bishop, Rook, Queen, King

class Board:
    def __init__(self):
        self._grid = [[None for _ in range(8)] for _ in range(8)]

    def get(self,pos):
        return self._grid[pos.row][pos.col]

    def set(self,pos,piece):
        self._grid[pos.row][pos.col] = piece

    def is_empty(self,pos):
        return self.get(pos) is None

    def setup_standard_position(self):
        back_rank = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for col, piece_cls in enumerate(back_rank):
            self.set(Position(0, col), piece_cls("white"))
            self.set(Position(7, col), piece_cls("black"))

        for col in range(8):
            self.set(Position(1, col), Pawn("white"))
            self.set(Position(6, col), Pawn("black"))
    

    def render(self) -> str:
        lines = []
        for row in range(7, -1, -1):
            row_cells = []
            for col in range(8):
                piece = self._grid[row][col]
                # WHY piece.symbol instead of str(piece): symbol is the
                # piece's own responsibility to define (polymorphism preview) —
                # Board doesn't need an if/elif chain checking piece type.
                row_cells.append(piece.symbol if piece else ".")
            lines.append(f"{row + 1}  " + " ".join(row_cells))
        lines.append("   " + " ".join("abcdefgh"))
        return "\n".join(lines)