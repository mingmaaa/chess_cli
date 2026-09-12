import copy

from .piece import Bishop, King, Knight, Pawn, Queen, Rook
from .position import Position
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
        raise ValueError(f"No {color} king on the board")

    def is_square_attacked(self,pos,by_color):
        for row in range(8):
            for col in range(8):
                piece = self._grid[row][col]
                if piece is not None and piece.color == by_color:
                    attacker_pos = Position(row,col)
                    if hasattr(piece, "get_attacked_squares"):
                        attacked = piece.get_attacked_squares(attacker_pos)
                    else:
                        attacked = piece.get_moves(self, attacker_pos)
                    if pos in attacked:
                        return True
        return False

    def clone(self):
        # this is way easier than manually reversing
        new_board = Board()
        new_board._grid = copy.deepcopy(self._grid)
        return new_board

    def is_in_check(self, color: str) -> bool:
        king_pos = self.find_king(color)
        enemy_color = "black" if color == "white" else "white"
        return self.is_square_attacked(king_pos, enemy_color)