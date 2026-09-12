from .position import Position

# ANSI codes
RESET = "\033[0m"
BOLD = "\033[1m"
BG_YELLOW = "\033[43m"
BG_BLUE = "\033[44m"
BG_DARK = "\033[48;5;238m"
BG_LIGHT = "\033[48;5;250m"
FG_WHITE = "\033[97m"
FG_BLACK = "\033[30m"


class Renderer:
    def __init__(self, use_color=True, use_unicode=True):
        self.use_color = use_color
        self.use_unicode = use_unicode

    def render(self, board, highlight_squares=None, captured_white=None, captured_black=None, current_color=None) -> str:
        highlight = set(highlight_squares or [])
        lines = []
        # header
        lines.append("    a  b  c  d  e  f  g  h")
        lines.append("   " + "-"*24)
        for row in range(7, -1, -1):
            row_str = f"{row+1} |"
            for col in range(8):
                pos = Position(row, col)
                piece = board.get(pos)
                symbol = piece.symbol if piece else " "
                # fallback if not unicode: use letter
                if not self.use_unicode and piece:
                    # map to letter
                    from .piece import Pawn, Knight, Bishop, Rook, Queen, King
                    if isinstance(piece, King):
                        symbol = "K" if piece.color == "white" else "k"
                    elif isinstance(piece, Queen):
                        symbol = "Q" if piece.color == "white" else "q"
                    elif isinstance(piece, Rook):
                        symbol = "R" if piece.color == "white" else "r"
                    elif isinstance(piece, Bishop):
                        symbol = "B" if piece.color == "white" else "b"
                    elif isinstance(piece, Knight):
                        symbol = "N" if piece.color == "white" else "n"
                    elif isinstance(piece, Pawn):
                        symbol = "P" if piece.color == "white" else "p"
                # square color
                is_light = (row + col) % 2 == 1
                bg = BG_LIGHT if is_light else BG_DARK
                if pos in highlight and self.use_color:
                    bg = BG_YELLOW
                if self.use_color:
                    cell = f"{bg} {symbol} {RESET}"
                else:
                    cell = f" {symbol} "
                row_str += cell
            row_str += f"| {row+1}"
            lines.append(row_str)
        lines.append("   " + "-"*24)
        lines.append("    a  b  c  d  e  f  g  h")
        if current_color:
            lines.append(f"\nTurn: {current_color} ({'White' if current_color=='white' else 'Black'})")
        if highlight:
            lines.append(f"Highlighted: {', '.join(str(p) for p in highlight)}")
        # captured tray placeholder
        if captured_white or captured_black:
            lines.append(f"Captured W: {captured_white} | B: {captured_black}")
        return "\n".join(lines)

    def render_with_legal(self, board, selected_pos, legal_moves):
        highlights = [m.to_pos for m in legal_moves]
        if selected_pos:
            highlights.append(selected_pos)
        return self.render(board, highlight_squares=highlights)
