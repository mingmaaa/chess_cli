# NOTES – OOP reflections

**Day1 – Encapsulation (Board._grid):** Kept `_grid` private behind `get`/`set`/`is_empty`. Swapping to dict would only touch `board.py:6` – callers never see storage.

**Day2 – Abstraction/Inheritance (Piece):** `Piece(ABC)` with `has_moved`/`symbol`/`get_moves` forces subclasses to implement contract. Instantiating `Piece` raises `TypeError` – proof abstraction is real.

**Day3 – Composition (Game has Board/Players):** `Game` *has* `Board` not *is* `Board`. Turn logic lives in `Game`, board stays dumb about players – good SRP.

**Day4 – Polymorphism (Pawn/Knight):** `Game.play_turn` calls `piece.get_moves` without `isinstance` branch. Adding Knight required zero change in `Game` – line `legal = self.get_legal_moves(from_pos)` stayed untouched.

**Day5 – Composition over inheritance (SlidingPiece):** One `SlidingPiece._slide` helper used by `Bishop`/`Rook`/`Queen` instead of copy-paste or multiple inheritance (`Queen` inheriting `Bishop+Rook` would be messy). Single extra level, not three copies.

**Day6 – Polymorphism at scale (check):** `is_square_attacked` reuses `get_moves` for all pieces; adding a new piece type needs no new check logic.

**Day7 – Clone vs mutate (legal filter):** `Board.clone()` deep copies `_grid` including `has_moved`. Filtering via clone avoids mutating real board and forgetting to revert fields – safer than `set` then manually undo.

**Day8 – Command pattern (Move):** `Move`/`CastleMove` with `apply`/`undo` let `Game` do `move.apply(board)` polymorphically. Castling moves both king+rook without `if castling:` in `Game`.

**Day9 – More Move subclasses:** `EnPassantMove` removes pawn not on destination, `PromotionMove` swaps piece class – zero change to `Game` core loop.

**Day10 – Dunder + history:** `Move.__str__` gives SAN `Nf3`/`O-O`, `Position.__str__` gives algebraic. `Game.history` + `undo` is trivial `pop().undo(board)` thanks to Command pattern.

**Day11 – Single responsibility (draws):** `position_key`/`is_insufficient_material` live in `Game` (tracks time) not `Board` (single position).

**Day12 – MVC (Renderer):** Moved `Board.render` logic to `Renderer.render(board, highlight_squares)` – model vs view boundary clear, can swap `Renderer` without touching rules.

**Day13 – Encapsulated serialization:** `Piece.to_dict`/`Board.to_dict`/`Game.save` keep serialization inside each class, not one giant external function poking `_grid`.

**Day14 – Testing contracts:** Tests assert `piece.get_moves` results not internal `_slide` details – refactor-safe. `perft` 20/400/8902 proves no hidden bugs.

**Day15 – Was it worth it?** Yes – each OOP pattern paid off when later rule (check, castling, undo, draws) required zero branching on piece type.
