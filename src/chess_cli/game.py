from .board import Board
from .player import Player
from .position import Position

class Game:
    def __init__(self,player_white,player_black):
        self.board = Board()
        self.board.setup_standard_position()
        self.players = {"white":player_white,"black": player_black}
        self.current_color = "white"

    @property
    def current_player(self):
        return self.players[self.current_color]

    def parse_input(self,text):
        from_str , to_str = text.strip().split()
        return Position.from_algebraic(from_str), Position.from_algebraic(to_str)

    def play_turn(self):
        print(self.board.render())
        print(f"\n{self.current_player.name}'s turn ({self.current_color})")
        text = input("Enter move (e.g. e2 e4): ")
        from_pos , to_pos = self.parse_input(text)
        piece = self.board.get(from_pos)

        if piece is None:
            print("No piece on that square. Try again...")
            return

        if piece.color != self.current_color:
            print("That's not your piece. Try again...")
            return

        legal_moves = self.get_legal_moves(from_pos)
        if to_pos not in legal_moves:
            print("Invalid move for that piece. Try again...")
            return
        captured = self.board.get(to_pos)
        self.board.set(to_pos,piece)
        self.board.set(from_pos,None)
        piece.has_moved = True
        if self.board.is_in_check("black" if self.current_color == "white" else "white"):
            print("Check!")
        self._switch_turn()

    def _switch_turn(self):
        self.current_color = "black" if self.current_color == "white" else "white"


    def run(self):
        print("currently no correct position validation logic.... ")
        while True:
            try:
                self.play_turn()
            except KeyboardInterrupt:
                print("Game Stopped!")
                break

    def get_legal_moves(self,pos):
        piece = self.board.get(pos)
        if piece is None:
            return []

        pseudo_legal = piece.get_moves(self.board,pos)
        legal = []

        for candidate in pseudo_legal:
            trial_board = self.board.clone()
            trial_board.set(candidate,trial_board.get(pos))
            trial_board.set(pos,None)

            if not trial_board.is_in_check(piece.color):
                legal.append(candidate)

        return legal
