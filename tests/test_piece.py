import sys
sys.path.insert(0, "src")
from chess_cli.position import Position
from chess_cli.board import Board
from chess_cli.piece import Pawn, Knight, Bishop, Rook, Queen, King

def empty_board():
    b = Board()
    for r in range(8):
        for c in range(8):
            b.set(Position(r,c), None)
    return b

def test_pawn_forward():
    b = empty_board()
    b.set(Position(1,4), Pawn("white"))
    moves = Pawn("white").get_moves(b, Position(1,4))
    assert Position(2,4) in moves
    assert Position(3,4) in moves

def test_pawn_blocked():
    b = empty_board()
    b.set(Position(1,4), Pawn("white"))
    b.set(Position(2,4), Pawn("black"))
    moves = Pawn("white").get_moves(b, Position(1,4))
    assert Position(2,4) not in moves

def test_pawn_capture():
    b = empty_board()
    b.set(Position(4,4), Pawn("white"))
    b.set(Position(5,3), Pawn("black"))
    moves = Pawn("white").get_moves(b, Position(4,4))
    assert Position(5,3) in moves
    assert Position(5,5) not in moves

def test_knight_moves():
    b = empty_board()
    b.set(Position(3,3), Knight("white"))
    moves = Knight("white").get_moves(b, Position(3,3))
    assert len(moves) == 8

def test_bishop_sliding():
    b = empty_board()
    b.set(Position(3,3), Bishop("white"))
    moves = Bishop("white").get_moves(b, Position(3,3))
    assert len(moves) == 13

def test_rook_blocked():
    b = empty_board()
    b.set(Position(0,0), Rook("white"))
    b.set(Position(0,1), Pawn("white"))
    moves = Rook("white").get_moves(b, Position(0,0))
    # should not slide past own pawn
    assert Position(0,2) not in moves
    assert Position(1,0) in moves

def test_queen_combined():
    b = empty_board()
    b.set(Position(3,3), Queen("white"))
    moves = Queen("white").get_moves(b, Position(3,3))
    assert len(moves) == 27

def test_king_one_step():
    b = empty_board()
    b.set(Position(4,4), King("white"))
    moves = King("white").get_moves(b, Position(4,4))
    assert len(moves) == 8
    # corner
    b2 = empty_board()
    b2.set(Position(0,0), King("white"))
    assert len(King("white").get_moves(b2, Position(0,0))) == 3
