import os
import pygame
import random
from src.fruit import Fruit

# ---------------------------------------------------------------------------
# Asset path helper
# ---------------------------------------------------------------------------
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def _asset(*parts):
    return os.path.join(_BASE_DIR, "assets", "images", *parts)


class FloatingText:
    """Renders floating score popups (+10, COMBO!) that drift upward and fade out."""
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


class GameScreen:
    """
    Main active Fruit Ninja gameplay screen.
    Handles fruit spawner, collision checks, particles, halves, scores, lives,
    countdown timer, background image, and heart-image HUD.
    """
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.score = 0
        self.lives = 5
        self.game_over = False
        self.time_remaining = 120.0  # 2-minute countdown

        # Fonts
        self.font = pygame.font.SysFont("Arial", 32, bold=True)
        self.title_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.sub_font = pygame.font.SysFont("Arial", 20)
        self.timer_font = pygame.font.SysFont("Arial", 36, bold=True)

        # Game object lists
        self.fruits = []
        self.sliced_halves = []
        self.particles = []
        self.floating_texts = []
        self.bg_stains_surface = pygame.Surface((width, height), pygame.SRCALPHA)

        self.spawn_timer = 0

        # --- Background image ---
        try:
            bg_raw = pygame.image.load(_asset("background-game.jpg")).convert()
            self.bg_image = pygame.transform.scale(bg_raw, (width, height))
        except Exception:
            self.bg_image = None  # fallback: solid fill

        # --- Heart images ---
        try:
            heart_raw = pygame.image.load(_asset("heart.jpg")).convert_alpha()
            self.heart_img = pygame.transform.smoothscale(heart_raw, (36, 36))
        except Exception:
            # Fallback: red circle surface
            self.heart_img = pygame.Surface((36, 36), pygame.SRCALPHA)
            pygame.draw.circle(self.heart_img, (220, 30, 30), (18, 18), 16)

        # Empty heart placeholder (dark red circle)
        self.heart_empty = pygame.Surface((36, 36), pygame.SRCALPHA)
        pygame.draw.circle(self.heart_empty, (60, 20, 20, 180), (18, 18), 16)
        pygame.draw.circle(self.heart_empty, (100, 40, 40, 200), (18, 18), 16, 2)

    # ------------------------------------------------------------------
    def reset(self):
        self.score = 0
        self.lives = 5
        self.game_over = False
        self.time_remaining = 120.0
        self.fruits.clear()
        self.sliced_halves.clear()
        self.particles.clear()
        self.floating_texts.clear()
        self.bg_stains_surface.fill((0, 0, 0, 0))
        self.spawn_timer = 0

    # ------------------------------------------------------------------
    def add_score(self, amount, x, y, label=None):
        self.score += amount
        txt = label if label else f"+{amount}"
        self.floating_texts.append(FloatingText(txt, x, y, self.font))

    def lose_life(self):
        self.lives -= 1
        if self.lives <= 0:
            self.lives = 0
            self.game_over = True

    def add_stain(self, x, y, color):
        radius = random.randint(25, 45)
        r, g, b = color[:3]
        stain_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(stain_surf, (r, g, b, 50), (radius, radius), radius)
        self.bg_stains_surface.blit(stain_surf, (x - radius, y - radius))

    # ------------------------------------------------------------------
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "menu"
            if self.game_over and event.key == pygame.K_r:
                self.reset()
        return None

    # ------------------------------------------------------------------
    def update(self, blade, dt):
        """Updates game state, handles fruit physics and blade slicing."""
        if not self.game_over:
            # Countdown timer
            self.time_remaining -= dt
            if self.time_remaining <= 0:
                self.time_remaining = 0
                self.game_over = True

            # Fruit Spawning
            self.spawn_timer += 1
            if self.spawn_timer > 55:
                self.fruits.append(Fruit(self.width, self.height))
                self.spawn_timer = 0

            blade_speed = blade.get_speed()

            for fruit in self.fruits[:]:
                fruit.update()

                # Slice collision check
                if not fruit.sliced and blade_speed > 8:
                    hit_radius = fruit.radius + (18 if not fruit.is_bomb else 8)
                    if blade.check_collision(fruit.x, fruit.y, hit_radius):
                        halves, new_particles = fruit.slice()
                        self.sliced_halves.extend(halves)
                        self.particles.extend(new_particles)

                        if fruit.is_bomb:
                            self.game_over = True
                        else:
                            self.add_score(10, fruit.x, fruit.y)
                            self.add_stain(fruit.x, fruit.y, fruit.juice_color)

                        self.fruits.remove(fruit)
                        continue

                # Missed fruit check
                if fruit.y > self.height + 60:
                    if not fruit.sliced and not fruit.is_bomb:
                        self.lose_life()
                    self.fruits.remove(fruit)

        # Update flying halves
        for half in self.sliced_halves[:]:
            half.update()
            if half.y > self.height + 80:
                self.sliced_halves.remove(half)

        # Update juice particles
        for p in self.particles[:]:
            p.update()
            if not p.is_alive():
                self.particles.remove(p)

        # Update floating scores
        for ft in self.floating_texts[:]:
            ft.update()
            if not ft.is_alive():
                self.floating_texts.remove(ft)

        return None

    # ------------------------------------------------------------------
    def _draw_hearts(self, surface):
        """Draw heart HUD in top-right corner."""
        spacing = 42
        total_hearts = 5
        start_x = self.width - 40 - (total_hearts * spacing)
        y = 22
        for i in range(total_hearts):
            x = start_x + i * spacing
            if i < self.lives:
                surface.blit(self.heart_img, (x, y))
            else:
                surface.blit(self.heart_empty, (x, y))

    def _draw_timer(self, surface):
        """Draw countdown timer in top-center with styled background box."""
        mins = int(self.time_remaining) // 60
        secs = int(self.time_remaining) % 60
        timer_str = f"{mins}:{secs:02d}"

        # Flashing red when < 20s
        if self.time_remaining < 20:
            flash = int(self.time_remaining * 2) % 2
            color = (255, 50, 50) if flash else (255, 180, 180)
        else:
            color = (255, 255, 255)

        timer_surf = self.timer_font.render(timer_str, True, color)
        tw, th = timer_surf.get_size()
        cx = self.width // 2
        box_w = tw + 28
        box_h = th + 12
        box_x = cx - box_w // 2
        box_y = 14

        # Dark semi-transparent rounded rect behind timer
        box_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        box_surf.fill((0, 0, 0, 0))
        pygame.draw.rect(box_surf, (10, 10, 20, 170), (0, 0, box_w, box_h), border_radius=12)
        surface.blit(box_surf, (box_x, box_y))

        surface.blit(timer_surf, (cx - tw // 2, box_y + 6))

    # ------------------------------------------------------------------
    def draw(self, surface):
        # Background image (or solid fallback)
        if self.bg_image:
            surface.blit(self.bg_image, (0, 0))
        else:
            surface.fill((15, 15, 25))

        # Juice stains on wall
        surface.blit(self.bg_stains_surface, (0, 0))

        # Active fruits
        for fruit in self.fruits:
            fruit.draw(surface)

        # Halves & particles
        for half in self.sliced_halves:
            half.draw(surface)

        for p in self.particles:
            p.draw(surface)

        # Floating score animations
        for ft in self.floating_texts:
            ft.draw(surface)

        # HUD Overlay
        if not self.game_over:
            # Score — top left
            score_surf = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
            surface.blit(score_surf, (25, 20))

            # Timer — top center
            self._draw_timer(surface)

            # Hearts — top right
            self._draw_hearts(surface)

        else:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((10, 10, 15, 180))
            surface.blit(overlay, (0, 0))

            # Determine game-over variant
            if self.time_remaining <= 0:
                over_text = "TIME'S UP!"
                over_color = (255, 220, 0)
            else:
                over_text = "GAME OVER"
                over_color = (255, 50, 50)

            over_surf = self.title_font.render(over_text, True, over_color)
            final_score = self.font.render(f"Final Score: {self.score}", True, (255, 215, 0))
            restart_surf = self.font.render("Press 'R' to Restart   |   [ESC] Main Menu", True, (255, 255, 255))

            surface.blit(over_surf, (self.width // 2 - over_surf.get_width() // 2, self.height // 2 - 70))
            surface.blit(final_score, (self.width // 2 - final_score.get_width() // 2, self.height // 2 - 10))
            surface.blit(restart_surf, (self.width // 2 - restart_surf.get_width() // 2, self.height // 2 + 50))
