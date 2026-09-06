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

    def get_moves(self,board,pos):
        return []

class Knight(Piece):
    @property
    def symbol(self):
        return "♘" if self.color == "white" else "♞"
    
    def get_moves(self,board,pos):
            return []
    

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
    