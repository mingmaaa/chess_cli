from position import Position
from abc import ABC, abstractmethod

class Piece(ABC):
    def __init__(self,color):
        self.color = color
        self.has_moved = False

    @property
    @abstractmethod
    def symbol(self):
        raise NotImplementedError

    @abstractmethod
    def get_moves(self,board,po):
        raise NotImplementedError

    def __repr__(self):
        return f"{self.__class__.__name__}({self.color})"

class Pawn(Piece):
    @property
    def symbol(self):
        return "♙" if self.color == "white" else "♟"

    def _in_bounds(self, pos):
        return 0 <= pos.row < 8 and 0 <= pos.col < 8

    def get_moves(self,board,pos):
        direction = 1 if self.color == "white" else -1
        moves = []
        one_step = Position(pos.row + direction,pos.col)
        if self._in_bounds(one_step) and board.is_empty(one_step):
            moves.append(one_step)

            if not self.has_moved:
                two_step = Position(pos.row+2*direction,pos.col)
                if self._in_bounds(two_step) and board.is_empty(two_step):
                    moves.append(two_step)

            for dc in (-1, 1):
                diag = Position(pos.row + direction, pos.col + dc)
                if self._in_bounds(diag) and not board.is_empty(diag):
                    target = board.get(diag)
                    if target.color != self.color:
                        moves.append(diag)

        return moves    



class Knight(Piece):
    @property
    def symbol(self):
        return "♘" if self.color == "white" else "♞"
    
    def get_moves(self,board,pos):
        offsets = [
            (2, 1), (2, -1), (-2, 1), (-2, -1),
            (1, 2), (1, -2), (-1, 2), (-1, -2),
        ]
        moves = []
        for dr, dc in offsets:
            target = Position(pos.row + dr, pos.col + dc)
            if not (0 <= target.row < 8 and 0 <= target.col < 8):
                continue
            occupant = board.get(target)
            if occupant is None or occupant.color != self.color:
                moves.append(target)
        return moves
    

class Bishop(Piece):
    @property
    def symbol(self) -> str:
        return "♗" if self.color == "white" else "♝"

    def get_moves(self,board,pos):
        return [] 


class Rook(Piece):
    @property
    def symbol(self) -> str:
        return "♖" if self.color == "white" else "♜"

    def get_moves(self,board,pos):
        return []


class Queen(Piece):
    @property
    def symbol(self) -> str:
        return "♕" if self.color == "white" else "♛"

    def get_moves(self,board,pos):
        return []


class King(Piece):
    @property
    def symbol(self) -> str:
        return "♔" if self.color == "white" else "♚"

    def get_moves(self,board,pos):
        return []
    