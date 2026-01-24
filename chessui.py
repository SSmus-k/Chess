import pygame
import random
import math
import time

pygame.font.init()

# ================= BACKGROUND =================

class Particle:
    def __init__(self, width, height):
        self.x = random.randint(0, width)
        self.y = random.randint(0, height)
        self.speed = random.uniform(0.2, 1)
        self.radius = random.randint(1, 3)

    def move(self, height):
        self.y += self.speed
        if self.y > height:
            self.y = 0

    def draw(self, screen):
        pygame.draw.circle(screen, (40, 40, 60), (int(self.x), int(self.y)), self.radius)


class AnimatedBackground:
    def __init__(self, width, height, count=80):
        self.particles = [Particle(width, height) for _ in range(count)]
        self.height = height

    def update(self):
        for p in self.particles:
            p.move(self.height)

    def draw(self, screen):
        screen.fill((15, 15, 25))
        for p in self.particles:
            p.draw(screen)

# ================= UI ELEMENTS =================

class Button:
    def __init__(self, text, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = pygame.font.SysFont(None, 36)

    def draw(self, screen):
        pygame.draw.rect(screen, (70, 70, 90), self.rect, border_radius=8)
        label = self.font.render(self.text, True, (255, 255, 255))
        screen.blit(label, label.get_rect(center=self.rect.center))

    def clicked(self, pos):
        return self.rect.collidepoint(pos)


class TextInput:
    def __init__(self, x, y, w, h, placeholder=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = ""
        self.active = False
        self.placeholder = placeholder
        self.font = pygame.font.SysFont(None, 32)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif len(self.text) < 12:
                self.text += event.unicode

    def draw(self, screen):
        pygame.draw.rect(screen, (90, 90, 110), self.rect, 2)
        display = self.text if self.text else self.placeholder
        label = self.font.render(display, True, (255, 255, 255))
        screen.blit(label, (self.rect.x + 5, self.rect.y + 5))


# ================= FLOATING PIECES =================

class FloatingPiece:
    def __init__(self, image, x, y):
        self.image = image
        self.x = x
        self.y = y
        self.base_y = y

    def draw(self, screen):
        offset = math.sin(time.time() * 2) * 5
        screen.blit(self.image, (self.x, self.base_y + offset))


# ================= THEMES =================

THEMES = {
    "Classic": {"light": (240,217,181), "dark": (181,136,99)},
    "Midnight": {"light": (70,70,90), "dark": (40,40,60)},
    "Emerald": {"light": (170,220,170), "dark": (60,120,60)}
}

def draw_theme_preview(screen, theme, x, y, size=20):
    colors = THEMES[theme]
    for r in range(4):
        for c in range(4):
            color = colors["light"] if (r+c)%2==0 else colors["dark"]
            pygame.draw.rect(screen, color, (x+c*size, y+r*size, size, size))


# ================= SCORE DISPLAY =================

class ScoreBoardUI:
    def __init__(self):
        self.font = pygame.font.SysFont(None, 28)

    def draw(self, screen, white_name, black_name, score):
        w = self.font.render(f"{white_name}: {score['w']}", True, (255,255,255))
        b = self.font.render(f"{black_name}: {score['b']}", True, (255,255,255))
        screen.blit(w, (20, 20))
        screen.blit(b, (20, 50))


# ================= MAIN MENU =================

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.bg = AnimatedBackground(*screen.get_size())

        self.start_btn = Button("Start Game", 300, 420, 200, 50)
        self.mode_btn = Button("Mode: AI", 300, 350, 200, 40)
        self.diff_btn = Button("Difficulty: Medium", 300, 300, 200, 40)
        self.theme_btn = Button("Theme: Classic", 300, 250, 200, 40)

        self.white_input = TextInput(250, 150, 300, 40, "White Player Name")
        self.black_input = TextInput(250, 200, 300, 40, "Black / AI Name")

        self.mode = "AI"
        self.difficulty = "Medium"
        self.theme = "Classic"

        self.difficulties = ["Easy", "Medium", "Hard"]
        self.themes = list(THEMES.keys())

        self.font = pygame.font.SysFont(None, 48)

    def run(self):
        clock = pygame.time.Clock()

        while True:
            clock.tick(60)
            self.bg.update()
            self.bg.draw(self.screen)

            title = self.font.render("CHESS", True, (255,255,255))
            self.screen.blit(title, title.get_rect(center=(400, 80)))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

                self.white_input.handle_event(event)
                self.black_input.handle_event(event)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.start_btn.clicked(event.pos):
                        return {
                            "white_name": self.white_input.text or "Player 1",
                            "black_name": self.black_input.text or ("AI" if self.mode=="AI" else "Player 2"),
                            "ai_depth": self.difficulties.index(self.difficulty) + 1,
                            "theme": self.theme,
                            "mode": self.mode
                        }

                    if self.mode_btn.clicked(event.pos):
                        self.mode = "Multiplayer" if self.mode=="AI" else "AI"
                        self.mode_btn.text = f"Mode: {self.mode}"

                    if self.diff_btn.clicked(event.pos):
                        i = (self.difficulties.index(self.difficulty)+1)%3
                        self.difficulty = self.difficulties[i]
                        self.diff_btn.text = f"Difficulty: {self.difficulty}"

                    if self.theme_btn.clicked(event.pos):
                        i = (self.themes.index(self.theme)+1)%len(self.themes)
                        self.theme = self.themes[i]
                        self.theme_btn.text = f"Theme: {self.theme}"

            self.white_input.draw(self.screen)
            self.black_input.draw(self.screen)

            self.start_btn.draw(self.screen)
            self.mode_btn.draw(self.screen)
            self.diff_btn.draw(self.screen)
            self.theme_btn.draw(self.screen)

            draw_theme_preview(self.screen, self.theme, 620, 260)

            pygame.display.flip()
