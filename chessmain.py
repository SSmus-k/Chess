import pygame as p
from chessengine import GameState, Move

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 60
IMAGES = {}
HIGHLIGHT_COLOR = (246, 246, 105, 120)  # soft yellow
clock = p.time.Clock()
gs=GameState()
validmoves = gs.getValidMoves()
movemade = False

# --------------------------------------------
# Load Piece Images from image folder
# --------------------------------------------
def load_images():
    pieces = ['wP', 'wR', 'wN', 'wB', 'wQ', 'wK',
              'bP', 'bR', 'bN', 'bB', 'bQ', 'bK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(
            p.image.load(f"images/{piece}.png"), (SQ_SIZE, SQ_SIZE)
        )


# --------------------------------------------
# Draw Chess Board (8x8)
# --------------------------------------------
def draw_board(screen):
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            square = p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            p.draw.rect(screen, color, square)


# --------------------------------------------
# Draw Pieces on Board (loading image pieces into the board)
# --------------------------------------------
def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


# --------------------------------------------
# Highlight Selected Square
# --------------------------------------------
def highlight_square(screen, sq):
    if sq == ():
        return
    
    r, c = sq
    highlight = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
    highlight.fill(HIGHLIGHT_COLOR)
    screen.blit(highlight, (c * SQ_SIZE, r * SQ_SIZE))


# --------------------------------------------
# Combine Board + Highlights + Pieces
# --------------------------------------------
def draw_game_state(screen, gs, sqSelected):
    draw_board(screen)
    highlight_square(screen, sqSelected)
    draw_pieces(screen, gs.board)


# --------------------------------------------
# Main Game Loop
# --------------------------------------------
def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    p.display.set_caption("Python Chess")
    clock = p.time.Clock()
    gs = GameState()
    load_images()

    running = True
    sqSelected = ()        # currently selected square
    playerClicks = []      # [first click, second click]
    movemade = False       # track if a move was made
    validmoves = gs.getValidMoves()

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE

                # Click same square twice → deselect
                if sqSelected == (row, col):
                    sqSelected = ()
                    playerClicks = []
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected)

                # If two clicks → try making a move
                if len(playerClicks) == 2:
                    move = Move(playerClicks[0], playerClicks[1], gs.board)
                    if move in validmoves:
                        gs.makeMove(move)
                        movemade = True
                    sqSelected = ()
                    playerClicks = []

            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo move when 'z' is pressed
                    gs.undoMove()
                    movemade = True

        # Update valid moves after a move is made
        if movemade:
            validmoves = gs.getValidMoves()
            movemade = False

        draw_game_state(screen, gs, sqSelected)
        clock.tick(MAX_FPS)
        p.display.flip()



if __name__ == "__main__":
    main()
