# Chess CLI

Two-player hotseat chess in the terminal – built as an OOP exercise in Python.

## Install

```bash
uv sync
# or pip install -e .
```

Requires Python 3.12+.

## Run

```bash
uv run chess-cli
# or
python -m chess_cli.main
```

You will be prompted for white/black player names.

## How Input Works

* Normal move: `e2 e4` (from square + to square)
* Castling: `O-O` (kingside) or `O-O-O` (queenside) or `e1 g1`
* Two-step: type `e2` then you will see highlighted legal destinations and be prompted for `e4`
* Undo: `undo`
* Promotion: when a pawn reaches last rank you will be prompted `Promote to (Q/R/B/N) [Q]:`
* Quit: `Ctrl+C`

The board uses unicode `♔♕♖♗♘♙` via `Renderer`. If your terminal does not support unicode, `Renderer(use_unicode=False)` falls back to `KQRBNP`.

## Example

```
    a  b  c  d  e  f  g  h
   ------------------------
8 | ♜ ♞ ♝ ♛ ♚ ♝ ♞ ♜ | 8
7 | ♟ ♟ ♟ ♟ ♟ ♟ ♟ ♟ | 7
6 |                 | 6
5 |                 | 5
4 |                 | 4
3 |                 | 3
2 | ♙ ♙ ♙ ♙ ♙ ♙ ♙ ♙ | 2
1 | ♖ ♘ ♗ ♕ ♔ ♗ ♘ ♖ | 1
   ------------------------
Turn: white (White)
```

## Save / Load / PGN

```python
from chess_cli.game import Game
from chess_cli.player import Player

g = Game(Player("Alice","white"), Player("Bob","black"))
# ... play ...
g.save("game.json")
g2 = Game.load("game.json")
g.export_pgn("game.pgn")
```

## Design Overview

* `Position` – frozen concept, `__eq__/__hash__/__repr__/__str__`, `from_algebraic`/`to_algebraic`
* `Piece` – abstract base (`abc.ABC`, `symbol`, `get_moves`), `has_moved`. Subclasses `Pawn`/`Knight`/`Bishop`/`Rook`/`Queen`/`King`. `SlidingPiece(Piece)` provides `_slide` helper for `Bishop`/`Rook`/`Queen` (composition over inheritance – one helper, not three copies)
* `Move` – Command pattern: `Move` base with `apply(board)`/`undo(board)`, subclasses `CastleMove`, `EnPassantMove`, `PromotionMove` each override polymorphically. `Game` calls `move.apply(board)` without `if castling:` branches.
* `Board` – model, private `_grid`, `get`/`set`/`is_empty`, `is_square_attacked`/`is_in_check` (polymorphism reuse), `clone` deep copy for simulation, `has_any_legal_moves`, `position_key` for draws, `to_dict`/`from_dict`.
* `Game` – controller/model, owns `Board` + 2 `Player`, `current_color`, `en_passant_target`, `history: list[Move]`, `halfmove_clock`, `repetition`. `get_legal_moves(pos)->list[Move]` filters via clone, `is_checkmate`/`is_stalemate`/`is_draw`, `save`/`load`/`export_pgn`, `perft`.
* `Renderer` – view, `render(board, highlight_squares)` ANSI/unicode, decoupled from `Board`.
* `Player` – thin data.

## Testing

```bash
pytest -q
# perft from start: depth1=20, depth2=400, depth3=8902
python -c "from chess_cli.game import Game; from chess_cli.player import Player; print(Game(Player('W','white'), Player('B','black')).perft(3))"
```

## Project Layout

```
src/chess_cli/
  position.py
  piece.py
  board.py
  move.py
  game.py
  renderer.py
  player.py
  main.py
tests/
  test_piece.py
  test_check.py
  test_perft.py
```

## Packaging

```bash
uv build
pip install dist/chess_cli-0.1.0-py3-none-any.whl
```
