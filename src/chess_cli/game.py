from .board import Board
from .move import CastleMove, EnPassantMove, Move, PromotionMove
from .piece import Bishop, King, Knight, Pawn, Queen, Rook
from .player import Player
from .position import Position


class Game:
    def __init__(self, player_white, player_black):
        self.board = Board()
        self.board.setup_standard_position()
        self.players = {"white": player_white, "black": player_black}
        self.current_color = "white"
        self.en_passant_target = None  # square that can be captured en passant
        self.history = []  # list[Move]
        self.halfmove_clock = 0
        self.repetition = {}
        self._halfmove_stack = []
        self._en_passant_stack = []
        # initial position
        key = self._position_key()
        self.repetition[key] = 1

    @property
    def current_player(self):
        return self.players[self.current_color]

    def parse_input(self, text):
        text = text.strip()
        # allow O-O and O-O-O for castling
        if text in ("O-O", "O-O-O", "0-0", "0-0-0"):
            return text
        parts = text.split()
        if len(parts) != 2:
            raise ValueError("Enter move as 'e2 e4' or 'O-O'")
        from_str, to_str = parts
        return Position.from_algebraic(from_str), Position.from_algebraic(to_str)

    def _generate_castling_moves(self, pos, king):
        moves = []
        if king.has_moved or self.board.is_in_check(king.color):
            return moves
        row = pos.row
        # kingside
        rook_k = self.board.get(Position(row, 7))
        if isinstance(rook_k, Rook) and not rook_k.has_moved:
            # squares f, g empty and not attacked
            if self.board.is_empty(Position(row, 5)) and self.board.is_empty(Position(row, 6)):
                if not self.board.is_square_attacked(Position(row, 5), "black" if king.color == "white" else "white"):
                    if not self.board.is_square_attacked(Position(row, 6), "black" if king.color == "white" else "white"):
                        moves.append(CastleMove(pos, Position(row, 6), Position(row, 7), Position(row, 5)))
        # queenside
        rook_q = self.board.get(Position(row, 0))
        if isinstance(rook_q, Rook) and not rook_q.has_moved:
            if self.board.is_empty(Position(row, 1)) and self.board.is_empty(Position(row, 2)) and self.board.is_empty(Position(row, 3)):
                if not self.board.is_square_attacked(Position(row, 2), "black" if king.color == "white" else "white"):
                    if not self.board.is_square_attacked(Position(row, 3), "black" if king.color == "white" else "white"):
                        moves.append(CastleMove(pos, Position(row, 2), Position(row, 0), Position(row, 3)))
        return moves

    def _generate_en_passant_moves(self, pos, pawn):
        moves = []
        if self.en_passant_target is None:
            return moves
        # pawn must be on correct rank and adjacent file
        # white pawns capture to row+1, black to row-1; target is behind double-pushed pawn
        for dc in (-1, 1):
            diag = Position(pos.row + (1 if pawn.color == "white" else -1), pos.col + dc)
            if diag == self.en_passant_target:
                # captured pawn is at same row as pawn, col = target col
                captured_pos = Position(pos.row, self.en_passant_target.col)
                target_piece = self.board.get(captured_pos)
                if target_piece and isinstance(target_piece, Pawn) and target_piece.color != pawn.color:
                    moves.append(EnPassantMove(pos, self.en_passant_target, captured_pos))
        return moves

    def get_legal_moves(self, pos):
        # returns list[Move] for that square, filtered for king safety
        piece = self.board.get(pos)
        if piece is None:
            return []
        pseudo_moves = []
        # normal pseudo-legal
        for target in piece.get_moves(self.board, pos):
            # promotion check
            if isinstance(piece, Pawn) and (target.row == 7 or target.row == 0):
                for promo_cls in (Queen, Rook, Bishop, Knight):
                    pseudo_moves.append(PromotionMove(pos, target, promo_cls))
            else:
                pseudo_moves.append(Move(pos, target))
        # castling
        if isinstance(piece, King):
            pseudo_moves.extend(self._generate_castling_moves(pos, piece))
        # en passant
        if isinstance(piece, Pawn):
            pseudo_moves.extend(self._generate_en_passant_moves(pos, piece))

        # filter for king safety via clone
        legal = []
        for mv in pseudo_moves:
            trial = self.board.clone()
            # need to simulate with same move semantics; we can use mv.apply on trial
            # need to handle promotion/clone etc; clone board has same pieces
            mv.apply(trial)
            if not trial.is_in_check(piece.color):
                legal.append(mv)
            mv.undo(trial)  # not needed as trial is discarded, but keep symmetry
        return legal

    def get_all_legal_moves(self, color):
        moves = []
        for row in range(8):
            for col in range(8):
                pos = Position(row, col)
                p = self.board.get(pos)
                if p and p.color == color:
                    moves.extend(self.get_legal_moves(pos))
        return moves

    def has_any_legal_moves(self, color):
        return len(self.get_all_legal_moves(color)) > 0

    def is_checkmate(self, color):
        return self.board.is_in_check(color) and not self.has_any_legal_moves(color)

    def is_stalemate(self, color):
        return not self.board.is_in_check(color) and not self.has_any_legal_moves(color)

    def _position_key(self):
        return self.board.position_key(self.en_passant_target, self.current_color)

    def is_insufficient_material(self):
        # K vs K, K+B vs K, K+N vs K, K+B vs K+B same color
        pieces = []
        bishops = []
        for row in range(8):
            for col in range(8):
                p = self.board.get(Position(row, col))
                if p:
                    pieces.append(p)
                    if isinstance(p, Bishop):
                        bishops.append(Position(row, col))
        if len(pieces) == 2:  # K vs K
            return True
        if len(pieces) == 3 and any(isinstance(p, (Bishop, Knight)) for p in pieces):
            return True
        if len(pieces) == 4 and all(isinstance(p, (King, Bishop)) for p in pieces):
            # K+B vs K+B – check same color bishop
            if len(bishops) == 2:
                # bishop square color: (row+col)%2
                c1 = (bishops[0].row + bishops[0].col) % 2
                c2 = (bishops[1].row + bishops[1].col) % 2
                if c1 == c2:
                    return True
        return False

    def is_threefold(self):
        # need at least 3 repetitions of same position
        key = self._position_key()
        return self.repetition.get(key, 0) >= 3

    def is_fifty_move(self):
        return self.halfmove_clock >= 100

    def is_draw(self):
        return self.is_stalemate(self.current_color) or self.is_insufficient_material() or self.is_threefold() or self.is_fifty_move()

    def play_turn(self):
        try:
            from .renderer import Renderer
            print(Renderer().render(self.board, current_color=self.current_color))
        except Exception:
            print(self.board.render())
        print(f"\n{self.current_player.name}'s turn ({self.current_color})")
        # check game over
        if self.is_checkmate(self.current_color):
            print(f"Checkmate! { 'black' if self.current_color=='white' else 'white'} wins.")
            return "checkmate"
        if self.is_stalemate(self.current_color):
            print("Stalemate! Draw.")
            return "draw"
        if self.is_threefold():
            print("Draw by threefold repetition!")
            return "draw"
        if self.is_fifty_move():
            print("Draw by fifty-move rule!")
            return "draw"
        if self.is_insufficient_material():
            print("Draw by insufficient material!")
            return "draw"
        text = input("Enter move (e.g. e2 e4, O-O, or 'undo'): ").strip()
        # two-step support: if single square, show highlights
        if len(text.split()) == 1 and len(text.strip()) == 2 and text.strip().lower() not in ("undo",):
            try:
                sel = Position.from_algebraic(text.strip())
                piece = self.board.get(sel)
                if piece and piece.color == self.current_color:
                    legal = self.get_legal_moves(sel)
                    try:
                        from .renderer import Renderer
                        print(Renderer().render_with_legal(self.board, sel, legal))
                    except Exception:
                        pass
                    if not legal:
                        print("No legal moves for that piece.")
                        return
                    dest_text = input(f"Legal: {', '.join(str(m.to_pos) for m in legal)} | Enter destination: ").strip()
                    if not dest_text:
                        return
                    # allow just destination like "e4"
                    if " " not in dest_text and len(dest_text) == 2:
                        text = f"{text.strip()} {dest_text}"
                    else:
                        text = f"{text.strip()} {dest_text}"
                # else fall through to normal parsing
            except Exception:
                pass
        if text.lower() == "undo":
            self.undo()
            return
        try:
            parsed = self.parse_input(text)
        except Exception as e:
            print(f"Invalid input: {e}")
            return
        # castling notation
        if isinstance(parsed, str):
            # find castle move among legal
            king_pos = self.board.find_king(self.current_color)
            legal = self.get_legal_moves(king_pos)
            castle = None
            for mv in legal:
                if isinstance(mv, CastleMove):
                    if (parsed in ("O-O", "0-0") and mv.to_pos.col == 6) or (parsed in ("O-O-O", "0-0-0") and mv.to_pos.col == 2):
                        castle = mv
                        break
            if castle:
                # handle promotion choice not needed
                self._apply_move(castle)
                return
            else:
                print("No legal castling that matches.")
                return
        from_pos, to_pos = parsed
        piece = self.board.get(from_pos)
        if piece is None:
            print("No piece on that square. Try again...")
            return
        if piece.color != self.current_color:
            print("That's not your piece. Try again...")
            return
        legal = self.get_legal_moves(from_pos)
        chosen = None
        for mv in legal:
            if mv.to_pos == to_pos:
                # if multiple promotion options, pick first queen or prompt
                if isinstance(mv, PromotionMove):
                    # if pawn promotion, ask choice if multiple
                    # For now, if to_pos is promotion rank, we already have Queen as first; but allow choice
                    # Check if there are multiple promo moves to same square, prompt
                    promo_moves = [m for m in legal if isinstance(m, PromotionMove) and m.to_pos == to_pos]
                    if len(promo_moves) > 1:
                        choice = input("Promote to (Q/R/B/N) [Q]: ").strip().upper() or "Q"
                        mapping = {"Q": Queen, "R": Rook, "B": Bishop, "N": Knight}
                        cls = mapping.get(choice, Queen)
                        for pm in promo_moves:
                            if pm.promotion_cls == cls:
                                chosen = pm
                                break
                        if not chosen:
                            chosen = promo_moves[0]
                    else:
                        chosen = mv
                    break
                else:
                    chosen = mv
                    break
        if not chosen:
            print("Invalid move for that piece. Try again...")
            return
        self._apply_move(chosen)

    def _apply_move(self, move):
        # save stacks for undo
        self._halfmove_stack.append(self.halfmove_clock)
        self._en_passant_stack.append(self.en_passant_target)
        # handle halfmove clock
        piece = self.board.get(move.from_pos)
        is_capture = move.captured is not None or isinstance(move, EnPassantMove)
        is_pawn = isinstance(piece, Pawn)
        # apply
        # need to capture before apply for halfmove? Already determined via board state
        # For PromotionMove, captured is set on apply; check beforehand via board.get
        captured_before = self.board.get(move.to_pos)
        # en passant capture also counts
        if isinstance(move, EnPassantMove):
            captured_before = move.captured_pawn if hasattr(move, 'captured_pawn') else self.board.get(move.captured_pos)  # before apply
        move.apply(self.board)
        self.history.append(move)
        # en passant target update
        if isinstance(piece, Pawn) and abs(move.to_pos.row - move.from_pos.row) == 2:
            # double push
            mid_row = (move.from_pos.row + move.to_pos.row)//2
            self.en_passant_target = Position(mid_row, move.from_pos.col)
        else:
            self.en_passant_target = None
        # halfmove
        if is_pawn or captured_before is not None or isinstance(move, EnPassantMove):
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1
        # switch turn first for position key (turn included)
        self._switch_turn()
        key = self._position_key()
        self.repetition[key] = self.repetition.get(key, 0) + 1
        # check
        opponent = "black" if self.current_color == "white" else "white"  # actually after switch, current is opponent, previous mover is opponent of current
        # after switch, current_color is opponent, previous mover is other
        mover = "black" if self.current_color == "white" else "white"
        if self.board.is_in_check(self.current_color):
            print("Check!")
        if self.is_checkmate(self.current_color):
            print(f"Checkmate! {mover} wins.")
        elif self.is_stalemate(self.current_color):
            print("Stalemate! Draw.")
        elif self.is_threefold():
            print("Draw by threefold repetition!")
        elif self.is_fifty_move():
            print("Draw by fifty-move rule!")
        elif self.is_insufficient_material():
            print("Draw by insufficient material!")

    def undo(self):
        if not self.history:
            print("No moves to undo.")
            return
        # revert repetition for current position
        key = self._position_key()
        if key in self.repetition:
            self.repetition[key] -= 1
            if self.repetition[key] <= 0:
                del self.repetition[key]
        move = self.history.pop()
        move.undo(self.board)
        # restore stacks
        if self._halfmove_stack:
            self.halfmove_clock = self._halfmove_stack.pop()
        if self._en_passant_stack:
            self.en_passant_target = self._en_passant_stack.pop()
        # switch back turn
        self._switch_turn()
        print(f"Undid {move}")

    def _switch_turn(self):
        self.current_color = "black" if self.current_color == "white" else "white"

    def run(self):
        print("Chess CLI – enter moves as 'e2 e4', 'O-O', or 'undo'. Ctrl+C to quit.")
        while True:
            try:
                res = self.play_turn()
                if res in ("checkmate", "draw"):
                    print(self.board.render())
                    print("Game over.")
                    break
            except KeyboardInterrupt:
                print("\nGame stopped!")
                break
            except Exception as e:
                print(f"Error: {e}")
