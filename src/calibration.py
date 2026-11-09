import pygame
import math

class CalibrationScanner:
    """
    Dedicated module for pre-game Index Finger Calibration.
    Locks user tracking, verifies camera reach and lighting,
    and displays an interactive hold-to-confirm progress target ring.
    """
    def __init__(self, screen_width, screen_height, target_radius=65, hold_duration=1.5):
        self.width = screen_width
        self.height = screen_height
        self.target_center = (screen_width // 2, screen_height // 2)
        self.target_radius = target_radius
        self.hold_duration = hold_duration  # Seconds required to hold still
        self.timer = 0.0
        self.is_complete = False

        self.title_font = pygame.font.SysFont("Arial", 44, bold=True)
        self.sub_font = pygame.font.SysFont("Arial", 22)

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
        """Resets calibration state for game restarts."""
        self.timer = 0.0
        self.is_complete = False

    def draw(self, surface):
        """Draws the dark overlay screen and target progress ring."""
        if self.is_complete:
            return

        # Semi-transparent dark overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((10, 10, 20, 190))
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