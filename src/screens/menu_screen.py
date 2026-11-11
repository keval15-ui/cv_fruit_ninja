import pygame
import os
import math

class MenuButton:
    """
    Interactive Button for Fruit Ninja Menu.
    Can be activated either by slicing/holding the fingertip or clicking the mouse.
    """
    def __init__(self, action_id, text, x, y, width, height, color=(0, 200, 255), icon=""):
        self.action_id = action_id
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.icon = icon
        self.hover_progress = 0.0  # 0.0 to 1.0 (holds to trigger)
        self.hold_threshold = 0.8  # seconds to hold or slice through
        self.is_hovered = False

    def update(self, pos, blade_speed, dt):
        """
        Updates button hover / slice status.
        Returns True if the button is triggered.
        """
        self.is_hovered = False
        if pos is not None and self.rect.collidepoint(pos):
            self.is_hovered = True
            
            # Instant trigger if sliced at speed!
            if blade_speed > 10:
                self.hover_progress = 1.0
                return True

            # Otherwise, hold-to-confirm progress
            self.hover_progress += dt / self.hold_threshold
            if self.hover_progress >= 1.0:
                self.hover_progress = 0.0
                return True
        else:
            self.hover_progress = max(0.0, self.hover_progress - dt * 2.5)

        return False

    def draw(self, surface, font, sub_font):
        # Draw background container
        bg_color = (25, 30, 45, 200) if not self.is_hovered else (45, 55, 80, 230)
        btn_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(btn_surf, bg_color, (0, 0, self.rect.width, self.rect.height), border_radius=16)

        # Border glow
        border_color = (0, 255, 200) if self.hover_progress > 0.5 else (self.color if self.is_hovered else (80, 100, 140))
        border_width = 3 if self.is_hovered else 2
        pygame.draw.rect(btn_surf, border_color, (0, 0, self.rect.width, self.rect.height), border_width, border_radius=16)

        # Hold/Slice progress fill
        if self.hover_progress > 0:
            fill_w = int(self.rect.width * self.hover_progress)
            fill_surf = pygame.Surface((fill_w, self.rect.height), pygame.SRCALPHA)
            fill_surf.fill((*self.color[:3], 90))
            btn_surf.blit(fill_surf, (0, 0))

        surface.blit(btn_surf, (self.rect.x, self.rect.y))

        # Text label
        txt_surf = font.render(self.text, True, (255, 255, 255))
        surface.blit(txt_surf, (self.rect.centerx - txt_surf.get_width() // 2, self.rect.centery - txt_surf.get_height() // 2 - 4))

        # Subtitle / Hint
        sub_text = "Slice or Hold" if self.is_hovered else "Point or Click"
        hint_surf = sub_font.render(sub_text, True, (180, 200, 220))
        surface.blit(hint_surf, (self.rect.centerx - hint_surf.get_width() // 2, self.rect.bottom - 22))


class MenuScreen:
    """
    Landing Page / Main Menu Screen.
    Contains options: START, BLADE, MULTIPLAYER.
    Uses background-landing.jpg as the backdrop.
    """
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.title_font = pygame.font.SysFont("Arial", 54, bold=True)
        self.btn_font = pygame.font.SysFont("Arial", 28, bold=True)
        self.sub_font = pygame.font.SysFont("Arial", 16)
        self.modal_font = pygame.font.SysFont("Arial", 24)

        # Load background-landing.jpg
        self.bg_image = None
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        bg_path = os.path.join(base_dir, "assets", "images", "background-landing.jpg")
        if os.path.exists(bg_path):
            try:
                raw_bg = pygame.image.load(bg_path).convert()
                self.bg_image = pygame.transform.smoothscale(raw_bg, (width, height))
            except Exception as e:
                print(f"[Warning] Failed to load landing background: {e}")

        # Setup Buttons: START, BLADE, MULTIPLAYER
        btn_w, btn_h = 280, 85
        spacing = 30
        total_w = (btn_w * 3) + (spacing * 2)
        start_x = (width - total_w) // 2
        btn_y = height // 2 + 60

        self.buttons = [
            MenuButton("start", "START GAME", start_x, btn_y, btn_w, btn_h, color=(0, 240, 255)),
            MenuButton("blade", "BLADE SELECT", start_x + (btn_w + spacing), btn_y, btn_w, btn_h, color=(255, 170, 0)),
            MenuButton("multiplayer", "MULTIPLAYER", start_x + (btn_w + spacing) * 2, btn_y, btn_w, btn_h, color=(255, 75, 130))
        ]

        self.info_modal = None
        self.modal_timer = 0.0

    def handle_event(self, event):
        """Allows mouse click navigation in addition to CV finger tracking."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for btn in self.buttons:
                if btn.rect.collidepoint((mx, my)):
                    return self._trigger_action(btn.action_id)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1 or event.key == pygame.K_s:
                return "start"
            elif event.key == pygame.K_2 or event.key == pygame.K_b:
                return "blade"
            elif event.key == pygame.K_3 or event.key == pygame.K_m:
                return self._trigger_action("multiplayer")
            elif event.key == pygame.K_ESCAPE and self.info_modal:
                self.info_modal = None

        return None

    def _trigger_action(self, action_id):
        if action_id == "multiplayer":
            self.info_modal = "MULTIPLAYER MODE (COMING SOON)\nDual-Camera / Split-Screen 2-Player Co-op!"
            self.modal_timer = 2.5
            return None
        return action_id

    def update(self, pos, blade_speed, dt):
        """
        Updates button interactions with fingertip tracking.
        Returns the next screen action ('start', 'blade', etc.) or None.
        """
        if self.info_modal:
            self.modal_timer -= dt
            if self.modal_timer <= 0:
                self.info_modal = None

        for btn in self.buttons:
            if btn.update(pos, blade_speed, dt):
                action = self._trigger_action(btn.action_id)
                if action:
                    return action

        return None

    def draw(self, surface):
        # 1. Render Landing Background
        if self.bg_image:
            surface.blit(self.bg_image, (0, 0))
        else:
            surface.fill((18, 18, 30))

        # 2. Translucent Overlay for contrast
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((10, 12, 24, 135))
        surface.blit(overlay, (0, 0))

        # 3. Main Title Banner
        title_surf = self.title_font.render("CV FRUIT NINJA", True, (0, 240, 255))
        glow_surf = self.title_font.render("CV FRUIT NINJA", True, (0, 180, 255))
        title_x = self.width // 2 - title_surf.get_width() // 2
        surface.blit(glow_surf, (title_x + 2, 92))
        surface.blit(title_surf, (title_x, 90))

        tagline = self.modal_font.render("Wave, Hold, or Slice to Select Your Mode", True, (210, 230, 245))
        surface.blit(tagline, (self.width // 2 - tagline.get_width() // 2, 160))

        # 4. Render Menu Buttons
        for btn in self.buttons:
            btn.draw(surface, self.btn_font, self.sub_font)

        # 5. Modal popup if triggered (e.g. Multiplayer notice)
        if self.info_modal:
            modal_rect = pygame.Rect(self.width // 2 - 250, self.height // 2 - 80, 500, 160)
            modal_surf = pygame.Surface((modal_rect.width, modal_rect.height), pygame.SRCALPHA)
            modal_surf.fill((15, 20, 35, 245))
            pygame.draw.rect(modal_surf, (255, 75, 130), (0, 0, modal_rect.width, modal_rect.height), 3, border_radius=16)
            surface.blit(modal_surf, (modal_rect.x, modal_rect.y))

            lines = self.info_modal.split("\n")
            for i, line in enumerate(lines):
                c = (255, 255, 255) if i == 0 else (200, 220, 240)
                txt = self.modal_font.render(line, True, c)
                surface.blit(txt, (modal_rect.centerx - txt.get_width() // 2, modal_rect.y + 40 + i * 40))
