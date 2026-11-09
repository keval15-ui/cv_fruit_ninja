import pygame
import random

class FloatingText:
    """
    Renders floating score popups (+10, COMBO!) that drift upward and fade out.
    """
    def __init__(self, text, x, y, font, color=(255, 215, 0)):
        self.text = text
        self.x = x
        self.y = y
        self.font = font
        self.color = color
        self.vy = -2.0
        self.alpha = 255

    def update(self):
        self.y += self.vy
        self.alpha -= 6

    def is_alive(self):
        return self.alpha > 0

    def draw(self, surface):
        if self.alpha > 0:
            text_surf = self.font.render(self.text, True, self.color)
            text_surf.set_alpha(max(0, self.alpha))
            surface.blit(text_surf, (self.x, self.y))


class GameManager:
    """
    Manages score, lives, game state transitions, juice stains, and HUD overlays.
    """
    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height
        
        self.score = 0
        self.lives = 3
        self.game_over = False
        
        self.font = pygame.font.SysFont("Arial", 32, bold=True)
        self.title_font = pygame.font.SysFont("Arial", 56, bold=True)
        
        self.floating_texts = []
        # Dedicated surface for baking persistent juice stains onto background
        self.bg_stains_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)

    def add_score(self, amount, x, y, text_override=None):
        """Increments score and spawns floating text popup."""
        self.score += amount
        label = text_override if text_override else f"+{amount}"
        self.floating_texts.append(FloatingText(label, x, y, self.font))

    def lose_life(self):
        """Reduces life count and triggers game over when lives reach zero."""
        self.lives -= 1
        if self.lives <= 0:
            self.game_over = True

    def add_stain(self, x, y, color):
        """Stamps a semi-transparent juice stain on the background surface."""
        radius = random.randint(25, 45)
        r, g, b = color[:3]
        stain_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(stain_surf, (r, g, b, 50), (radius, radius), radius)
        self.bg_stains_surface.blit(stain_surf, (x - radius, y - radius))

    def reset(self):
        """Resets all game parameters for restart."""
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.floating_texts.clear()
        self.bg_stains_surface.fill((0, 0, 0, 0))

    def update(self):
        """Updates all floating UI texts."""
        for ft in self.floating_texts[:]:
            ft.update()
            if not ft.is_alive():
                self.floating_texts.remove(ft)

    def draw_ui(self, surface):
        """Draws background stains, floating text popups, and HUD overlays."""
        surface.blit(self.bg_stains_surface, (0, 0))

        for ft in self.floating_texts:
            ft.draw(surface)

        # Score & Lives HUD
        score_surf = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        lives_surf = self.font.render(f"Lives: {'X ' * max(0, self.lives)}", True, (255, 50, 50))
        surface.blit(score_surf, (25, 20))
        surface.blit(lives_surf, (self.width - 200, 20))

        # Game Over Screen Overlay
        if self.game_over:
            over_surf = self.title_font.render("GAME OVER", True, (255, 50, 50))
            restart_surf = self.font.render("Press 'R' to Restart", True, (255, 255, 255))
            surface.blit(over_surf, (self.width // 2 - 150, self.height // 2 - 50))
            surface.blit(restart_surf, (self.width // 2 - 130, self.height // 2 + 20))