from .position import Position


class Move:
    def __init__(self, from_pos: Position, to_pos: Position):
        self.from_pos = from_pos
        self.to_pos = to_pos
        self.captured = None
        self.moved_piece = None
        self.prev_has_moved = None

    def apply(self, board):
        self.moved_piece = board.get(self.from_pos)
        self.captured = board.get(self.to_pos)
        self.prev_has_moved = getattr(self.moved_piece, "has_moved", None) if self.moved_piece else None
        board.set(self.to_pos, self.moved_piece)
        board.set(self.from_pos, None)
        if self.moved_piece is not None:
            self.moved_piece.has_moved = True

    def undo(self, board):
        board.set(self.from_pos, self.moved_piece)
        board.set(self.to_pos, self.captured)
        if self.moved_piece is not None and self.prev_has_moved is not None:
            self.moved_piece.has_moved = self.prev_has_moved

    def __repr__(self):
        cap = f"x{self.to_pos}" if self.captured else f"{self.to_pos}"
        return f"{self.__class__.__name__}({self.from_pos}->{self.to_pos})"

    def __str__(self):
        # base SAN: e.g., e2-e4, N f3; subclasses override
        c = self.captured is not None
        sep = "x" if c else "-"
        return f"{self.from_pos}{sep}{self.to_pos}"

    def __eq__(self, other):
        return isinstance(other, Move) and self.from_pos == other.from_pos and self.to_pos == other.to_pos and type(self) == type(other)


class CastleMove(Move):
    def __init__(self, from_pos: Position, to_pos: Position, rook_from: Position, rook_to: Position):
        super().__init__(from_pos, to_pos)
        self.rook_from = rook_from
        self.rook_to = rook_to
        self.rook_piece = None
        self.rook_prev_has_moved = None
        self.king_prev_has_moved = None

    def apply(self, board):
        # king
        self.moved_piece = board.get(self.from_pos)
        self.captured = None  # castling never captures
        self.king_prev_has_moved = getattr(self.moved_piece, "has_moved", None)
        self.rook_piece = board.get(self.rook_from)
        self.rook_prev_has_moved = getattr(self.rook_piece, "has_moved", None) if self.rook_piece else None
        # move king
        board.set(self.to_pos, self.moved_piece)
        board.set(self.from_pos, None)
        if self.moved_piece:
            self.moved_piece.has_moved = True
        # move rook
        board.set(self.rook_to, self.rook_piece)
        board.set(self.rook_from, None)
        if self.rook_piece:
            self.rook_piece.has_moved = True

    def undo(self, board):
        # undo rook first
        board.set(self.rook_from, self.rook_piece)
        board.set(self.rook_to, None)
        if self.rook_piece and self.rook_prev_has_moved is not None:
            self.rook_piece.has_moved = self.rook_prev_has_moved
        # undo king
        board.set(self.from_pos, self.moved_piece)
        board.set(self.to_pos, self.captured)
        if self.moved_piece and self.king_prev_has_moved is not None:
            self.moved_piece.has_moved = self.king_prev_has_moved

    def __str__(self):
        # O-O or O-O-O
        if self.to_pos.col == 6:  # g-file kingside
            return "O-O"
        else:
            return "O-O-O"


class EnPassantMove(Move):
    def __init__(self, from_pos: Position, to_pos: Position, captured_pos: Position):
        super().__init__(from_pos, to_pos)
        self.captured_pos = captured_pos
        self.captured_pawn = None

    def apply(self, board):
        self.moved_piece = board.get(self.from_pos)
        self.prev_has_moved = getattr(self.moved_piece, "has_moved", None) if self.moved_piece else None
        self.captured_pawn = board.get(self.captured_pos)
        self.captured = self.captured_pawn
        board.set(self.to_pos, self.moved_piece)
        board.set(self.from_pos, None)
        board.set(self.captured_pos, None)
        if self.moved_piece:
            self.moved_piece.has_moved = True

    def undo(self, board):
        board.set(self.from_pos, self.moved_piece)
        board.set(self.to_pos, None)
        board.set(self.captured_pos, self.captured_pawn)
        if self.moved_piece and self.prev_has_moved is not None:
            self.moved_piece.has_moved = self.prev_has_moved

    def __str__(self):
        # exd6 notation simplified as file x to
        return f"{chr(ord('a')+self.from_pos.col)}x{self.to_pos}"


class PromotionMove(Move):
    def __init__(self, from_pos: Position, to_pos: Position, promotion_cls, captured=None):
        super().__init__(from_pos, to_pos)
        self.promotion_cls = promotion_cls
        self.promoted_piece = None
        self.original_pawn = None

    def apply(self, board):
        self.original_pawn = board.get(self.from_pos)
        self.captured = board.get(self.to_pos)
        self.prev_has_moved = getattr(self.original_pawn, "has_moved", None) if self.original_pawn else None
        # create promoted piece with same color
        if self.original_pawn:
            self.promoted_piece = self.promotion_cls(self.original_pawn.color)
            self.promoted_piece.has_moved = True
        board.set(self.to_pos, self.promoted_piece)
        board.set(self.from_pos, None)

    def undo(self, board):
        board.set(self.from_pos, self.original_pawn)
        board.set(self.to_pos, self.captured)
        if self.original_pawn and self.prev_has_moved is not None:
            self.original_pawn.has_moved = self.prev_has_moved

    def __str__(self):
        piece_letter = self.promotion_cls.__name__[0]
        # Queen -> Q, but Knight is N
        if self.promotion_cls.__name__ == "Knight":
            piece_letter = "N"
        promo = f"={piece_letter}"
        if self.captured:
            return f"{chr(ord('a')+self.from_pos.col)}x{self.to_pos}{promo}"
        return f"{self.to_pos}{promo}"
