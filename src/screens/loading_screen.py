import pygame
import os

class LoadingScreen:
    """
    Initial loading screen displaying background and assets initialization progress.
    """
    def __init__(self, width, height, duration=1.2):
        self.width = width
        self.height = height
        self.duration = duration
        self.elapsed = 0.0
        self.is_finished = False

        self.title_font = pygame.font.SysFont("Arial", 42, bold=True)
        self.sub_font = pygame.font.SysFont("Arial", 22)

        # Load background
        self.bg_image = None
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        bg_path = os.path.join(base_dir, "assets", "images", "background-loading.jpg")
        if os.path.exists(bg_path):
            try:
                raw_bg = pygame.image.load(bg_path).convert()
                self.bg_image = pygame.transform.smoothscale(raw_bg, (width, height))
            except Exception as e:
                print(f"[Warning] Failed to load loading background: {e}")

    def reset(self):
        self.elapsed = 0.0
        self.is_finished = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            self.is_finished = True

    def update(self, dt):
        if not self.is_finished:
            self.elapsed += dt
            if self.elapsed >= self.duration:
                self.is_finished = True

    def draw(self, surface):
        if self.bg_image:
            surface.blit(self.bg_image, (0, 0))
        else:
            surface.fill((15, 15, 25))

        # Soft overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((10, 10, 20, 150))
        surface.blit(overlay, (0, 0))

        # Title
        title_surf = self.title_font.render("CV FRUIT NINJA", True, (0, 240, 255))
        surface.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, self.height // 2 - 90))

        # Progress bar
        bar_w = 360
        bar_h = 16
        bar_x = self.width // 2 - bar_w // 2
        bar_y = self.height // 2 + 10
        ratio = min(1.0, self.elapsed / max(0.01, self.duration))

        pygame.draw.rect(surface, (40, 40, 60), (bar_x, bar_y, bar_w, bar_h), border_radius=8)
        if ratio > 0:
            fill_w = int(bar_w * ratio)
            pygame.draw.rect(surface, (0, 240, 255), (bar_x, bar_y, fill_w, bar_h), border_radius=8)
        pygame.draw.rect(surface, (100, 200, 255), (bar_x, bar_y, bar_w, bar_h), 2, border_radius=8)

        status_text = "INITIALIZING SENSORS & SYSTEM..." if ratio < 0.95 else "READY!"
        sub_surf = self.sub_font.render(status_text, True, (220, 220, 220))
        surface.blit(sub_surf, (self.width // 2 - sub_surf.get_width() // 2, bar_y + 35))
