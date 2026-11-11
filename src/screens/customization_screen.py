import pygame
import os

class CustomizationScreen:
    """
    Screen to preview and select Blade colors and trail styles.
    """
    BLADE_PALETTES = [
        {"name": "CYAN LASER", "outer": (0, 240, 255), "inner": (255, 255, 255)},
        {"name": "CRIMSON FURY", "outer": (255, 45, 80), "inner": (255, 200, 210)},
        {"name": "GOLDEN SUN", "outer": (255, 195, 0), "inner": (255, 255, 240)},
        {"name": "EMERALD BLADE", "outer": (0, 255, 130), "inner": (220, 255, 235)},
        {"name": "VIOLET VOID", "outer": (180, 50, 255), "inner": (255, 220, 255)},
    ]

    def __init__(self, width, height, current_palette_index=0):
        self.width = width
        self.height = height
        self.selected_index = current_palette_index

        self.title_font = pygame.font.SysFont("Arial", 46, bold=True)
        self.card_font = pygame.font.SysFont("Arial", 22, bold=True)
        self.sub_font = pygame.font.SysFont("Arial", 18)

        # Background (reusing landing background)
        self.bg_image = None
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        bg_path = os.path.join(base_dir, "assets", "images", "background-landing.jpg")
        if os.path.exists(bg_path):
            try:
                raw_bg = pygame.image.load(bg_path).convert()
                self.bg_image = pygame.transform.smoothscale(raw_bg, (width, height))
            except Exception as e:
                print(f"[Warning] Failed to load customization background: {e}")

        # Card geometry
        card_w, card_h = 160, 200
        spacing = 20
        total_w = len(self.BLADE_PALETTES) * card_w + (len(self.BLADE_PALETTES) - 1) * spacing
        start_x = (width - total_w) // 2
        card_y = height // 2 - 60

        self.cards = []
        for i, pal in enumerate(self.BLADE_PALETTES):
            rect = pygame.Rect(start_x + i * (card_w + spacing), card_y, card_w, card_h)
            self.cards.append({"rect": rect, "palette": pal, "hover": 0.0})

        # Back button
        self.back_rect = pygame.Rect(40, 40, 140, 48)
        self.back_hover = 0.0

    def get_selected_blade_colors(self):
        pal = self.BLADE_PALETTES[self.selected_index]
        return pal["outer"], pal["inner"]

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_b):
                return "back"
            elif event.key == pygame.K_LEFT:
                self.selected_index = (self.selected_index - 1) % len(self.BLADE_PALETTES)
            elif event.key == pygame.K_RIGHT:
                self.selected_index = (self.selected_index + 1) % len(self.BLADE_PALETTES)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if self.back_rect.collidepoint((mx, my)):
                return "back"
            for i, card in enumerate(self.cards):
                if card["rect"].collidepoint((mx, my)):
                    self.selected_index = i

        return None

    def update(self, pos, blade_speed, dt):
        """Allows selecting a blade by slicing/hovering over cards."""
        if pos is not None:
            # Check back button
            if self.back_rect.collidepoint(pos):
                self.back_hover += dt / 0.6
                if self.back_hover >= 1.0 or blade_speed > 10:
                    self.back_hover = 0.0
                    return "back"
            else:
                self.back_hover = max(0.0, self.back_hover - dt * 2.0)

            # Check cards
            for i, card in enumerate(self.cards):
                if card["rect"].collidepoint(pos):
                    card["hover"] += dt / 0.5
                    if card["hover"] >= 1.0 or blade_speed > 10:
                        self.selected_index = i
                        card["hover"] = 0.0
                else:
                    card["hover"] = max(0.0, card["hover"] - dt * 2.0)

        return None

    def draw(self, surface):
        if self.bg_image:
            surface.blit(self.bg_image, (0, 0))
        else:
            surface.fill((18, 18, 28))

        # Overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((10, 12, 24, 155))
        surface.blit(overlay, (0, 0))

        # Title
        title_surf = self.title_font.render("BLADE CUSTOMIZATION", True, (0, 240, 255))
        surface.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 45))

        # Back Button
        bg_col = (45, 55, 80, 220) if self.back_hover > 0 else (25, 30, 45, 180)
        back_surf = pygame.Surface((self.back_rect.width, self.back_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(back_surf, bg_col, (0, 0, self.back_rect.width, self.back_rect.height), border_radius=10)
        pygame.draw.rect(back_surf, (0, 240, 255), (0, 0, self.back_rect.width, self.back_rect.height), 2, border_radius=10)
        surface.blit(back_surf, (self.back_rect.x, self.back_rect.y))

        back_txt = self.sub_font.render("< BACK", True, (255, 255, 255))
        surface.blit(back_txt, (self.back_rect.centerx - back_txt.get_width() // 2, self.back_rect.centery - back_txt.get_height() // 2))

        # Palette cards
        for i, card in enumerate(self.cards):
            r = card["rect"]
            pal = card["palette"]
            is_active = (i == self.selected_index)

            c_surf = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
            bg = (35, 42, 60, 230) if is_active else (20, 25, 38, 180)
            pygame.draw.rect(c_surf, bg, (0, 0, r.width, r.height), border_radius=12)

            border_c = pal["outer"] if is_active else (60, 75, 100)
            border_w = 3 if is_active else 1
            pygame.draw.rect(c_surf, border_c, (0, 0, r.width, r.height), border_w, border_radius=12)

            # Draw preview blade line inside card
            cx, cy = r.width // 2, 80
            pygame.draw.line(c_surf, pal["outer"], (cx - 40, cy + 30), (cx + 40, cy - 30), 8)
            pygame.draw.line(c_surf, pal["inner"], (cx - 40, cy + 30), (cx + 40, cy - 30), 3)

            surface.blit(c_surf, (r.x, r.y))

            # Text
            name_surf = self.card_font.render(pal["name"], True, pal["outer"] if is_active else (200, 200, 200))
            surface.blit(name_surf, (r.centerx - name_surf.get_width() // 2, r.bottom - 45))

            if is_active:
                tag = self.sub_font.render("[EQUIPPED]", True, (0, 255, 150))
                surface.blit(tag, (r.centerx - tag.get_width() // 2, r.bottom - 22))

        # Hint text
        hint = self.sub_font.render("Slice or click any blade to equip it. Press ESC or click BACK to return.", True, (170, 180, 200))
        surface.blit(hint, (self.width // 2 - hint.get_width() // 2, self.height - 60))
