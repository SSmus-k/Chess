import pygame
import random
import math
import time

pygame.font.init()
pygame.init()

# ================= CONSTANTS & ASSETS =================

WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess of Aeons")

# Colors
GOLD = (255, 215, 0)
CYAN = (0, 255, 255)
WHITE = (255, 255, 255)
DARK_OVERLAY = (20, 20, 30, 180) # The 4th number is transparency (0-255)
GLOW_COLOR = (200, 200, 255)

# Try to load the background image you have, otherwise use a dark fill
try:
    BG_IMAGE = pygame.image.load("background.png") # SAVE THE GENERATED IMAGE AS THIS NAME
    BG_IMAGE = pygame.transform.scale(BG_IMAGE, (WIDTH, HEIGHT))
except:
    BG_IMAGE = None

# ================= EFFECTS & UTILS =================

def draw_text_with_glow(surface, text, font, color, center_pos, glow_color=(255,255,255), radius=2):
    """Draws text with a blurred shadow/glow effect."""
    text_surf = font.render(text, True, color)
    rect = text_surf.get_rect(center=center_pos)
    
    # Draw glow (simple offset method)
    for dx, dy in [(-radius, 0), (radius, 0), (0, -radius), (0, radius)]:
        glow = font.render(text, True, glow_color)
        glow.set_alpha(100)
        surface.blit(glow, (rect.x + dx, rect.y + dy))
        
    surface.blit(text_surf, rect)

class Particle:
    """Updated to look like magical embers/dust"""
    def __init__(self, width, height):
        self.x = random.randint(0, width)
        self.y = random.randint(0, height)
        self.speed = random.uniform(0.2, 0.8)
        self.radius = random.randint(1, 2)
        self.alpha = random.randint(50, 200)

    def move(self, height):
        self.y -= self.speed # Float upwards like embers
        self.x += math.sin(time.time() + self.y * 0.01) * 0.5 # Wiggle
        if self.y < 0:
            self.y = height
            self.x = random.randint(0, WIDTH)

    def draw(self, screen):
        # Create a small surface for alpha transparency
        s = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 200, 100, self.alpha), (self.radius, self.radius), self.radius)
        screen.blit(s, (self.x, self.y))

class AnimatedBackground:
    def __init__(self, width, height, count=50):
        self.particles = [Particle(width, height) for _ in range(count)]
        self.height = height

    def update(self):
        for p in self.particles:
            p.move(self.height)

    def draw(self, screen):
        if BG_IMAGE:
            screen.blit(BG_IMAGE, (0, 0))
        else:
            screen.fill((15, 10, 25)) # Fallback dark purple
        
        # Overlay a subtle dark gradient at the bottom for readability
        gradient = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(gradient, (0,0,0,100), (0, 0, WIDTH, HEIGHT))
        screen.blit(gradient, (0,0))

        for p in self.particles:
            p.draw(screen)

# ================= UI ELEMENTS (MODERN STYLE) =================

class GlassPanel:
    """The glowing container for the UI"""
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.surface = pygame.Surface((w, h), pygame.SRCALPHA)
        self.border_color = (255, 255, 255, 50)
        
    def draw(self, screen):
        # Draw semi-transparent background
        pygame.draw.rect(self.surface, (20, 20, 30, 200), self.surface.get_rect(), border_radius=20)
        
        # Draw glowing border
        pygame.draw.rect(self.surface, self.border_color, self.surface.get_rect(), 2, border_radius=20)
        
        screen.blit(self.surface, self.rect.topleft)

class ModernButton:
    def __init__(self, text, x, y, w, h, base_color=(0, 150, 255), hover_color=(50, 200, 255)):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = pygame.font.Font(None, 32)
        self.base_color = base_color
        self.hover_color = hover_color
        self.current_color = base_color
        self.is_hovered = False

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        self.current_color = self.hover_color if self.is_hovered else self.base_color

    def clicked(self, pos):
        return self.rect.collidepoint(pos)

    def draw(self, screen):
        # Draw button shadow
        shadow_rect = self.rect.copy()
        shadow_rect.y += 4
        pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect, border_radius=25)

        # Draw main button body
        pygame.draw.rect(screen, self.current_color, self.rect, border_radius=25)
        
        # Draw shiny top highlight (glass effect on button)
        highlight = pygame.Surface((self.rect.width - 10, self.rect.height//2), pygame.SRCALPHA)
        pygame.draw.ellipse(highlight, (255, 255, 255, 50), highlight.get_rect())
        screen.blit(highlight, (self.rect.x + 5, self.rect.y + 2))

        # Text
        text_surf = self.font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

class ModernTextInput:
    def __init__(self, x, y, w, h, placeholder=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = ""
        self.active = False
        self.placeholder = placeholder
        self.font = pygame.font.Font(None, 28)
        self.color_inactive = (100, 100, 120)
        self.color_active = (255, 215, 0) # Gold when active

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif len(self.text) < 15:
                self.text += event.unicode

    def draw(self, screen):
        # Draw background input box
        color = self.color_active if self.active else self.color_inactive
        
        # Background
        pygame.draw.rect(screen, (30, 30, 40), self.rect, border_radius=10)
        # Border
        pygame.draw.rect(screen, color, self.rect, 2, border_radius=10)

        display_text = self.text if self.text else self.placeholder
        text_color = WHITE if self.text else (150, 150, 150)
        
        surface = self.font.render(display_text, True, text_color)
        
        # Center vertically
        text_y = self.rect.y + (self.rect.height - surface.get_height()) // 2
        screen.blit(surface, (self.rect.x + 10, text_y))


# ================= MAIN MENU =================

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.bg = AnimatedBackground(WIDTH, HEIGHT)
        
        # Center coordinates
        cx = WIDTH // 2
        
        # The Glass Container
        self.panel = GlassPanel(cx - 200, 100, 400, 450)

        # Inputs
        self.white_input = ModernTextInput(cx - 150, 220, 300, 40, "White Player Name")
        self.black_input = ModernTextInput(cx - 150, 280, 300, 40, "Black Player / AI")

        # Buttons (Using colors from the image reference)
        # Blue "Play" Button
        self.start_btn = ModernButton("START GAME", cx - 150, 470, 300, 50, base_color=(0, 120, 200), hover_color=(0, 160, 255))
        
        # Gold/Yellow "Settings/Mode" Buttons
        self.mode_btn = ModernButton("Mode: AI", cx - 150, 340, 140, 40, base_color=(180, 140, 50), hover_color=(220, 180, 70))
        self.diff_btn = ModernButton("Medium", cx + 10, 340, 140, 40, base_color=(180, 140, 50), hover_color=(220, 180, 70))
        self.theme_btn = ModernButton("Theme: Classic", cx - 150, 400, 300, 40, base_color=(80, 80, 100), hover_color=(100, 100, 120))

        # State
        self.mode = "AI"
        self.difficulty = "Medium"
        self.theme = "Classic"
        self.difficulties = ["Easy", "Medium", "Hard"]
        self.themes = ["Classic", "Midnight", "Emerald"]

        # Fonts
        self.title_font = pygame.font.Font(None, 70)
        self.subtitle_font = pygame.font.Font(None, 30)

    def run(self):
        clock = pygame.time.Clock()

        while True:
            clock.tick(60)
            mouse_pos = pygame.mouse.get_pos()
            
            # 1. Update Background
            self.bg.update()
            self.bg.draw(self.screen)

            # 2. Draw Glass Panel Container
            self.panel.draw(self.screen)

            # 3. Draw Title (Gold Text)
            draw_text_with_glow(self.screen, "CHESS", self.title_font, GOLD, (WIDTH//2, 140), glow_color=(100,80,0))
            draw_text_with_glow(self.screen, "OF AEONS", self.subtitle_font, (200, 200, 200), (WIDTH//2, 180))

            # 4. Handle Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return None
                
                self.white_input.handle_event(event)
                self.black_input.handle_event(event)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.start_btn.clicked(event.pos):
                        return {
                            "white": self.white_input.text,
                            "black": self.black_input.text,
                            "mode": self.mode,
                            "diff": self.difficulty,
                            "theme": self.theme
                        }
                    
                    if self.mode_btn.clicked(event.pos):
                        self.mode = "Multiplayer" if self.mode == "AI" else "AI"
                        self.mode_btn.text = f"Mode: {self.mode}"
                    
                    if self.diff_btn.clicked(event.pos):
                        curr_idx = self.difficulties.index(self.difficulty)
                        self.difficulty = self.difficulties[(curr_idx + 1) % 3]
                        self.diff_btn.text = f"{self.difficulty}"

                    if self.theme_btn.clicked(event.pos):
                        curr_idx = self.themes.index(self.theme)
                        self.theme = self.themes[(curr_idx + 1) % len(self.themes)]
                        self.theme_btn.text = f"Theme: {self.theme}"

            # 5. Check Hovers
            self.start_btn.check_hover(mouse_pos)
            self.mode_btn.check_hover(mouse_pos)
            self.diff_btn.check_hover(mouse_pos)
            self.theme_btn.check_hover(mouse_pos)

            # 6. Draw UI Elements
            self.white_input.draw(self.screen)
            self.black_input.draw(self.screen)
            
            self.mode_btn.draw(self.screen)
            self.diff_btn.draw(self.screen)
            self.theme_btn.draw(self.screen)
            self.start_btn.draw(self.screen)

            pygame.display.flip()

# ================= EXECUTION =================

if __name__ == "__main__":
    menu = MainMenu(SCREEN)
    settings = menu.run()
    
    if settings:
        print("Game Started with:", settings)
        # Your game loop would start here
    
    pygame.quit()