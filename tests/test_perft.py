import sys
sys.path.insert(0, "src")
from chess_cli.game import Game
from chess_cli.player import Player

def test_perft():
    g = Game(Player("W","white"), Player("B","black"))
    assert g.perft(1) == 20
    assert g.perft(2) == 400
    assert g.perft(3) == 8902
