from board import Board
from player import Player
from game import Game

if __name__ == "__main__":
    white = Player(name=input("White player's name: "), color="white")
    black = Player(name=input("Black player's name: "), color="black")
    game = Game(white, black)
    game.run()