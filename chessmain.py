import pygame
import os
from chessui import MainMenu, AnimatedBackground
from chessengine import ChessEngine, Move

# Configuration
WIDTH, HEIGHT = 800, 600
BOARD_SIZE = 480
SQ_SIZE = BOARD_SIZE // 8
BOARD_X, BOARD_Y = 50, 60

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        base_path = os.path.join(os.path.dirname(__file__), "assets", "sounds")
        self.move_sound = pygame.mixer.Sound(os.path.join(base_path, "move.WAV"))
        self.capture_sound = pygame.mixer.Sound(os.path.join(base_path, "capture.WAV"))
        
        # Load and play background music
        try:
            pygame.mixer.music.load(os.path.join(base_path, "bg_music.mp3"))
            pygame.mixer.music.set_volume(0.4)
            pygame.mixer.music.play(-1)
        except:
            print("Music file not found.")

def load_images():
    pieces = ['P','R','N','B','Q','K']
    images = {}
    path = os.path.join(os.path.dirname(__file__), "assets", "images")
    for color in ['w', 'b']:
        for p in pieces:
            # Match your filenames (bp.png, wp.png etc)
            filename = f"{color}{p.lower() if p=='P' else p}.png"
            img_path = os.path.join(path, filename)
            if os.path.exists(img_path):
                images[color + p] = pygame.transform.scale(pygame.image.load(img_path).convert_alpha(), (SQ_SIZE, SQ_SIZE))
    return images

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    images = load_images()
    sounds = SoundManager()
    menu = MainMenu(screen)
    bg_anim = AnimatedBackground(WIDTH, HEIGHT)

    while True:
        settings = menu.run()
        if not settings: break
        
        engine = ChessEngine()
        running = True
        selected_sq = None

        while running:
            bg_anim.update()
            bg_anim.draw(screen)
            
            # Draw Board & Pieces
            # (Your existing draw_board and draw_pieces logic goes here)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); return
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    if BOARD_X <= mx <= BOARD_X + BOARD_SIZE and BOARD_Y <= my <= BOARD_Y + BOARD_SIZE:
                        col, row = (mx - BOARD_X) // SQ_SIZE, (my - BOARD_Y) // SQ_SIZE
                        
                        if selected_sq == (row, col):
                            selected_sq = None
                        elif selected_sq is None:
                            if engine.board[row][col]: # Select only if piece exists
                                selected_sq = (row, col)
                        else:
                            move = engine.get_move(selected_sq, (row, col))
                            if move:
                                if move.captured:
                                    sounds.capture_sound.play()
                                else:
                                    sounds.move_sound.play()
                                engine.make_move(move)
                            selected_sq = None

            pygame.display.flip()

if __name__ == "__main__":
    main()