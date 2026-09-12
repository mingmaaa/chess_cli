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
                row_cells.append(piece.symbol if piece else ".")
            lines.append(f"{row + 1}  " + " ".join(row_cells))
        lines.append("   " + " ".join("abcdefgh"))
        return "\n".join(lines)

    def find_king(self,color):
        for row in range(8):
            for col in range(8):
                piece = self._grid[row][col]
                if piece is not None and piece.color == color and isinstance(piece,King):
                    return Position(row,col)
        return ValueError(f"No {color} king on the board")


    def _is_square_attacked(self,pos,by_color):
        for row in range(8):
            for col in range(8):
                piece = self._grid[row][col]
                if piece is not None and self.color == by_color:
                    attacker_pos = Position(row,col)
                    if pos in piece.get_moves(self,attacker_pos):
                        return True
        return False
