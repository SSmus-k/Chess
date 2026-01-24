import pygame
from chessui import MainMenu, ScoreBoardUI, THEMES
from chessengine import ChessEngine
import os
WIDTH, HEIGHT = 800, 600
BOARD_SIZE = 480
SQ_SIZE = BOARD_SIZE // 8
BOARD_X = 50
BOARD_Y = 60


def draw_board(screen, theme):
    colors = THEMES[theme]
    for r in range(8):
        for c in range(8):
            color = colors["light"] if (r + c) % 2 == 0 else colors["dark"]
            pygame.draw.rect(
                screen,
                color,
                (BOARD_X + c * SQ_SIZE, BOARD_Y + r * SQ_SIZE, SQ_SIZE, SQ_SIZE),
            )


def draw_pieces(screen, board, images):
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece:
                p_type, color = piece
                img = images[color + p_type]
                screen.blit(img, (BOARD_X + c * SQ_SIZE, BOARD_Y + r * SQ_SIZE))


def load_images():
    pieces = ['P','R','N','B','Q','K']
    images = {}
    base_path = os.path.dirname(os.path.abspath(__file__))
    images_path = os.path.join(base_path, "assets", "images")

    for color in ['w', 'b']:
        for p in pieces:
            filename = f"{color}{p}.png"
            path = os.path.join(images_path, filename)

            if not os.path.exists(path):
                print(f"Missing image: {path}")
                continue

            images[color + p] = pygame.transform.scale(
                pygame.image.load(path).convert_alpha(),
                (SQ_SIZE, SQ_SIZE)
            )

    return images


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess")

    images = load_images()
    menu = MainMenu(screen)

    while True:
        settings = menu.run()
        engine = ChessEngine()
        scoreboard = ScoreBoardUI()

        clock = pygame.time.Clock()
        running = True
        selected_square = None

        while running:
            clock.tick(60)
            screen.fill((20, 20, 30))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    if BOARD_X <= mx <= BOARD_X + BOARD_SIZE and BOARD_Y <= my <= BOARD_Y + BOARD_SIZE:
                        col = (mx - BOARD_X) // SQ_SIZE
                        row = (my - BOARD_Y) // SQ_SIZE

                        if selected_square is None:
                            selected_square = (row, col)
                        else:
                            engine.make_move(selected_square, (row, col))
                            selected_square = None

            # Draw everything
            draw_board(screen, settings["theme"])
            draw_pieces(screen, engine.board, images)
            scoreboard.draw(screen, settings["white_name"], settings["black_name"], engine.score)

            pygame.display.flip()


if __name__ == "__main__":
    main()
