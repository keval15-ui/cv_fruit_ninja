import pygame
import math
import os
import random

class CalibrationScreen:
    """
    Dedicated screen for pre-game Index Finger Calibration.
    Enhanced with dynamic holographic radar sweep, rotating calibration ticks,
    ambient glow, and pulse animations over calibration.jpg.
    """
    def __init__(self, screen_width, screen_height, target_radius=75, hold_duration=1.5):
        self.width = screen_width
        self.height = screen_height
        self.target_center = (screen_width // 2, screen_height // 2 + 15)
        self.target_radius = target_radius
        self.hold_duration = hold_duration
        self.timer = 0.0
        self.is_complete = False

        # Visual animation parameters
        self.sweep_angle = 0.0
        self.ring_pulse = 0.0

        self.title_font = pygame.font.SysFont("Arial", 46, bold=True)
        self.sub_font = pygame.font.SysFont("Arial", 22)
        self.status_font = pygame.font.SysFont("Arial", 24, bold=True)
        self.micro_font = pygame.font.SysFont("Arial", 15)

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
        self.sweep_angle += dt * 3.5
        self.ring_pulse += dt * 2.0

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
        self.timer = 0.0
        self.is_complete = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN):
            self.is_complete = True

    def draw(self, surface):
        cx, cy = self.target_center
        progress = min(1.0, self.timer / self.hold_duration)
        active_color = (0, 255, 160) if progress > 0.8 else (0, 240, 255)

        # 1. Background image
        if self.bg_image:
            surface.blit(self.bg_image, (0, 0))
        else:
            surface.fill((14, 16, 26))

        # 2. Tech grid vignette overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((8, 12, 22, 145))
        surface.blit(overlay, (0, 0))

        # 3. Header Title & Instructions
        title_surf = self.title_font.render("HOLOGRAPHIC SENSOR CALIBRATION", True, (0, 240, 255))
        glow_title = self.title_font.render("HOLOGRAPHIC SENSOR CALIBRATION", True, (0, 160, 255))
        title_x = self.width // 2 - title_surf.get_width() // 2
        surface.blit(glow_title, (title_x + 1, 61))
        surface.blit(title_surf, (title_x, 60))

        sub_surf = self.sub_font.render(
            "Align your index fingertip inside the optical ring to synchronize motion tracking",
            True, (210, 225, 240)
        )
        surface.blit(sub_surf, (self.width // 2 - sub_surf.get_width() // 2, 115))

        # 4. Outer Holographic Reticle Ring with Animated Ticks
        outer_reticle_r = self.target_radius + 36
        num_ticks = 24
        for i in range(num_ticks):
            angle = (i / num_ticks) * (math.pi * 2) + self.sweep_angle * 0.3
            tick_len = 10 if i % 4 == 0 else 5
            x1 = cx + math.cos(angle) * outer_reticle_r
            y1 = cy + math.sin(angle) * outer_reticle_r
            x2 = cx + math.cos(angle) * (outer_reticle_r + tick_len)
            y2 = cy + math.sin(angle) * (outer_reticle_r + tick_len)
            col = active_color if i % 4 == 0 else (60, 90, 130)
            pygame.draw.line(surface, col, (x1, y1), (x2, y2), 2)

        # Concentric guide circles
        pulse_offset = math.sin(self.ring_pulse) * 3
        pygame.draw.circle(surface, (45, 65, 95), (cx, cy), int(self.target_radius + 20 + pulse_offset), 1)
        pygame.draw.circle(surface, (30, 45, 70), (cx, cy), self.target_radius, 2)

        # 5. Radar Sweep Line
        sweep_len = self.target_radius + 15
        sx = cx + math.cos(self.sweep_angle) * sweep_len
        sy = cy + math.sin(self.sweep_angle) * sweep_len
        pygame.draw.line(surface, (*active_color, 180), (cx, cy), (sx, sy), 2)

        # 6. Radial Filling Progress
        if progress > 0:
            fill_radius = int(self.target_radius * progress)
            fill_surf = pygame.Surface((fill_radius * 2 + 4, fill_radius * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(fill_surf, (*active_color, 110), (fill_radius + 2, fill_radius + 2), fill_radius)
            surface.blit(fill_surf, (cx - fill_radius - 2, cy - fill_radius - 2))

            # Outer arc glow indicator
            arc_rect = pygame.Rect(cx - self.target_radius - 8, cy - self.target_radius - 8, (self.target_radius + 8) * 2, (self.target_radius + 8) * 2)
            pygame.draw.arc(surface, active_color, arc_rect, -math.pi / 2, -math.pi / 2 + progress * (math.pi * 2), 4)

        # Main active ring border
        pygame.draw.circle(surface, active_color, (cx, cy), self.target_radius + 8, 2)

        # 7. Center Status Text & Percentage
        if progress > 0:
            status_txt = f"LOCKING {int(progress * 100)}%"
            txt_surf = self.status_font.render(status_txt, True, (255, 255, 255))
        else:
            txt_surf = self.status_font.render("POINT HERE", True, (0, 240, 255))

        surface.blit(txt_surf, (cx - txt_surf.get_width() // 2, cy - txt_surf.get_height() // 2))

        # Micro sub-hint
        hint_label = "HOLD STEADY" if progress > 0 else "TARGET ACQUISITION"
        hl_surf = self.micro_font.render(hint_label, True, (180, 200, 220))
        surface.blit(hl_surf, (cx - hl_surf.get_width() // 2, cy + 24))

        # Bottom Skip Hint
        skip_surf = self.micro_font.render("Press SPACE or ENTER to bypass calibration", True, (140, 155, 175))
        surface.blit(skip_surf, (self.width // 2 - skip_surf.get_width() // 2, self.height - 45))
