import pygame
import math
import os

class CalibrationScreen:
    """
    Dedicated screen for pre-game Index Finger Calibration.
    Locks user tracking, verifies camera reach and lighting,
    and displays an interactive hold-to-confirm progress target ring
    with calibration.jpg as the background.
    """
    def __init__(self, screen_width, screen_height, target_radius=65, hold_duration=1.5):
        self.width = screen_width
        self.height = screen_height
        self.target_center = (screen_width // 2, screen_height // 2)
        self.target_radius = target_radius
        self.hold_duration = hold_duration
        self.timer = 0.0
        self.is_complete = False

        self.title_font = pygame.font.SysFont("Arial", 44, bold=True)
        self.sub_font = pygame.font.SysFont("Arial", 22)

        # Load calibration background image
        self.bg_image = None
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        bg_path = os.path.join(base_dir, "assets", "images", "calibration.jpg")
        if os.path.exists(bg_path):
            try:
                loaded_bg = pygame.image.load(bg_path).convert()
                self.bg_image = pygame.transform.smoothscale(loaded_bg, (screen_width, screen_height))
            except Exception as e:
                print(f"[Warning] Failed to load calibration background image: {e}")
                self.bg_image = None

    def update(self, pos, dt):
        """
        Updates the calibration timer.
        Returns True when calibration completes successfully.
        """
        if self.is_complete:
            return True

        if pos is None:
            self.timer = max(0.0, self.timer - dt * 2.0)
            return False

        dist = math.hypot(pos[0] - self.target_center[0], pos[1] - self.target_center[1])
        if dist <= self.target_radius:
            self.timer += dt
            if self.timer >= self.hold_duration:
                self.is_complete = True
                return True
        else:
            self.timer = max(0.0, self.timer - dt * 2.0)

        return False

    def reset(self):
        """Resets calibration state."""
        self.timer = 0.0
        self.is_complete = False

    def handle_event(self, event):
        # Allow pressing Space or Enter to skip calibration if user prefers
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN):
            self.is_complete = True

    def draw(self, surface):
        """Draws the calibration background, dark overlay, and target progress ring."""
        if self.bg_image:
            surface.blit(self.bg_image, (0, 0))
        else:
            surface.fill((15, 15, 25))

        # Semi-transparent dark overlay for high contrast and readability
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((10, 10, 20, 140))
        surface.blit(overlay, (0, 0))

        # Title & Instructions
        title_surf = self.title_font.render("INDEX FINGER SCANNER", True, (0, 240, 255))
        sub_surf = self.sub_font.render(
            "Place your index finger inside the ring to lock calibration & test tracking", 
            True, (200, 200, 200)
        )
        surface.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 70))
        surface.blit(sub_surf, (self.width // 2 - sub_surf.get_width() // 2, 130))

        # Render Target Ring
        cx, cy = self.target_center
        progress = min(1.0, self.timer / self.hold_duration)
        ring_color = (0, 255, 150) if progress > 0.9 else (0, 240, 255)

        pygame.draw.circle(surface, (50, 50, 75), (cx, cy), self.target_radius, 4)
        pygame.draw.circle(surface, ring_color, (cx, cy), self.target_radius + 8, 2)

        # Draw Filling Progress Circle
        if progress > 0:
            fill_radius = int(self.target_radius * progress)
            pygame.draw.circle(surface, (*ring_color, 120), (cx, cy), fill_radius)

        # Center Status Text
        status_txt = "HOLD STILL" if progress > 0 else "POINT HERE"
        txt_surf = self.sub_font.render(status_txt, True, (255, 255, 255))
        surface.blit(txt_surf, (cx - txt_surf.get_width() // 2, cy - txt_surf.get_height() // 2))

        # Skip hint
        hint_surf = self.sub_font.render("(Press SPACE or ENTER to skip)", True, (150, 150, 170))
        surface.blit(hint_surf, (self.width // 2 - hint_surf.get_width() // 2, self.height - 50))
