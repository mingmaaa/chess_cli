from board import Board

if __name__ == "__main__":
    b = Board()
    b.setup_standard_position()
    print(b.render())