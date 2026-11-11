import pygame
import random
from src.fruit import Fruit

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
    Handles fruit spawner, collision checks, particles, halves, scores, and lives.
    """
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.score = 0
        self.lives = 5
        self.game_over = False

        self.font = pygame.font.SysFont("Arial", 32, bold=True)
        self.title_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.sub_font = pygame.font.SysFont("Arial", 20)

        self.fruits = []
        self.sliced_halves = []
        self.particles = []
        self.floating_texts = []
        self.bg_stains_surface = pygame.Surface((width, height), pygame.SRCALPHA)

        self.spawn_timer = 0

    def reset(self):
        self.score = 0
        self.lives = 5
        self.game_over = False
        self.fruits.clear()
        self.sliced_halves.clear()
        self.particles.clear()
        self.floating_texts.clear()
        self.bg_stains_surface.fill((0, 0, 0, 0))
        self.spawn_timer = 0

    def add_score(self, amount, x, y, label=None):
        self.score += amount
        txt = label if label else f"+{amount}"
        self.floating_texts.append(FloatingText(txt, x, y, self.font))

    def lose_life(self):
        self.lives -= 1
        if self.lives <= 0:
            self.game_over = True

    def add_stain(self, x, y, color):
        radius = random.randint(25, 45)
        r, g, b = color[:3]
        stain_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(stain_surf, (r, g, b, 50), (radius, radius), radius)
        self.bg_stains_surface.blit(stain_surf, (x - radius, y - radius))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "menu"
            if self.game_over and event.key == pygame.K_r:
                self.reset()
        return None

    def update(self, blade):
        """Updates game state, handles fruit physics and blade slicing."""
        if not self.game_over:
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

    def draw(self, surface):
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
            score_surf = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
            lives_surf = self.font.render(f"Lives: {'X ' * max(0, self.lives)}", True, (255, 50, 50))
            esc_hint = self.sub_font.render("[ESC] Menu", True, (130, 140, 160))
            surface.blit(score_surf, (25, 20))
            surface.blit(lives_surf, (self.width - 220, 20))
            surface.blit(esc_hint, (25, 65))
        else:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((10, 10, 15, 180))
            surface.blit(overlay, (0, 0))

            over_surf = self.title_font.render("GAME OVER", True, (255, 50, 50))
            restart_surf = self.font.render("Press 'R' to Restart   |   [ESC] Main Menu", True, (255, 255, 255))
            final_score = self.font.render(f"Final Score: {self.score}", True, (255, 215, 0))

            surface.blit(over_surf, (self.width // 2 - over_surf.get_width() // 2, self.height // 2 - 70))
            surface.blit(final_score, (self.width // 2 - final_score.get_width() // 2, self.height // 2 - 10))
            surface.blit(restart_surf, (self.width // 2 - restart_surf.get_width() // 2, self.height // 2 + 50))
