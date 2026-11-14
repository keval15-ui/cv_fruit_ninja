import pygame
import os
import math
import random

class AmbientOrb:
    """Floating particles on menus for lively visuals."""
    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.reset()

    def reset(self):
        self.x = random.uniform(0, self.screen_w)
        self.y = random.uniform(self.screen_h, self.screen_h + 100)
        self.radius = random.uniform(2, 6)
        self.speed = random.uniform(20, 50)
        self.angle = random.uniform(0, math.pi * 2)
        self.color = random.choice([
            (30, 125, 225),
            (235, 170, 35),
            (235, 75, 45),
            (70, 165, 75)
        ])
        self.alpha = random.randint(60, 160)

    def update(self, dt):
        self.y -= self.speed * dt
        self.x += math.sin(self.angle) * 0.5
        self.angle += dt * 1.5
        if self.y < -20:
            self.reset()

    def draw(self, surface):
        s = pygame.Surface((int(self.radius * 2 + 2), int(self.radius * 2 + 2)), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, int(self.alpha)), (int(self.radius + 1), int(self.radius + 1)), int(self.radius))
        surface.blit(s, (int(self.x - self.radius), int(self.y - self.radius)))


class CircleMenuButton:
    """
    Circular Fruit-Ninja style Menu Button.
    Features:
    - Glowing concentric circular rings
    - Pulsing breathing animation
    - Slice-through detection & hold-to-confirm radial progress arc
    - Mouse click & CV finger tracking support
    """
    def __init__(self, action_id, title, subtitle, cx, cy, radius=95, theme_color=(30, 125, 225), badge=""):
        self.action_id = action_id
        self.title = title
        self.subtitle = subtitle
        self.cx = cx
        self.cy = cy
        self.base_radius = radius
        self.radius = radius
        self.theme_color = theme_color
        self.badge = badge

        self.hover_progress = 0.0
        self.hold_threshold = 0.7  # seconds to trigger on hold
        self.is_hovered = False
        self.pulse_phase = random.uniform(0, math.pi * 2)

    def collide_point(self, pt):
        return math.hypot(pt[0] - self.cx, pt[1] - self.cy) <= self.radius

    def update(self, pos, blade_speed, dt):
        self.pulse_phase += dt * 2.5
        self.is_hovered = False

        if pos is not None and self.collide_point(pos):
            self.is_hovered = True

            # Instant trigger if sliced through at speed!
            if blade_speed > 9:
                self.hover_progress = 1.0
                return True

            # Hold to trigger
            self.hover_progress += dt / self.hold_threshold
            if self.hover_progress >= 1.0:
                self.hover_progress = 0.0
                return True
        else:
            self.hover_progress = max(0.0, self.hover_progress - dt * 2.5)

        # Subtle smooth scale on hover
        target_r = self.base_radius + (12 if self.is_hovered else 0)
        self.radius += (target_r - self.radius) * min(1.0, dt * 10)

        return False

    def draw(self, surface, title_font, sub_font, small_font):
        cx, cy = int(self.cx), int(self.cy)
        r = int(self.radius)

        # 1. Subtle Outer Glow
        glow_radius = int(r + 15 + math.sin(self.pulse_phase) * 4)
        glow_surf = pygame.Surface((glow_radius * 2 + 4, glow_radius * 2 + 4), pygame.SRCALPHA)
        glow_alpha = 45 if not self.is_hovered else 85
        pygame.draw.circle(
            glow_surf,
            (*self.theme_color[:3], glow_alpha),
            (glow_radius + 2, glow_radius + 2),
            glow_radius
        )
        surface.blit(glow_surf, (cx - glow_radius - 2, cy - glow_radius - 2))

        # 2. Translucent Circular Orb Body
        body_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        bg_alpha = 230 if self.is_hovered else 190
        base_fill = (20, 24, 38, bg_alpha)
        pygame.draw.circle(body_surf, base_fill, (r + 2, r + 2), r)

        # Inner subtle gradient / highlight on top
        highlight_rect = pygame.Rect(r - int(r * 0.6) + 2, 8, int(r * 1.2), int(r * 0.5))
        pygame.draw.ellipse(body_surf, (255, 255, 255, 25), highlight_rect)

        # 3. Holding/Slicing Radial Progress Fill
        if self.hover_progress > 0:
            fill_r = int(r * self.hover_progress)
            pygame.draw.circle(body_surf, (*self.theme_color[:3], 95), (r + 2, r + 2), fill_r)

        # 4. Ring Borders
        ring_color = (255, 255, 255) if self.is_hovered else self.theme_color
        border_w = 4 if self.is_hovered else 3
        pygame.draw.circle(body_surf, ring_color, (r + 2, r + 2), r, border_w)

        # Dotted / dashed decorative inner ring
        inner_r = max(10, r - 10)
        pygame.draw.circle(body_surf, (*self.theme_color[:3], 120), (r + 2, r + 2), inner_r, 1)

        surface.blit(body_surf, (cx - r - 2, cy - r - 2))

        # 5. Progress Arc Overlay when holding
        if self.hover_progress > 0.05:
            arc_rect = pygame.Rect(cx - r - 6, cy - r - 6, (r + 6) * 2, (r + 6) * 2)
            angle_span = self.hover_progress * (math.pi * 2)
            # Pygame arc draws counterclockwise from 0 (3 o'clock)
            pygame.draw.arc(surface, self.theme_color, arc_rect, -math.pi / 2, -math.pi / 2 + angle_span, 5)

        # 6. Button Text & Subtitle
        t_surf = title_font.render(self.title, True, (255, 255, 255))
        surface.blit(t_surf, (cx - t_surf.get_width() // 2, cy - t_surf.get_height() // 2 - 12))

        sub_col = self.theme_color if self.is_hovered else (220, 215, 195)
        s_surf = sub_font.render(self.subtitle, True, sub_col)
        surface.blit(s_surf, (cx - s_surf.get_width() // 2, cy + 14))

        # Action Instruction
        hint_txt = "SLICE or HOLD" if self.is_hovered else "SLICE"
        hint_surf = small_font.render(hint_txt, True, (160, 180, 200))
        surface.blit(hint_surf, (cx - hint_surf.get_width() // 2, cy + 36))

        # Badge pill (if any)
        if self.badge:
            badge_surf = small_font.render(self.badge, True, (255, 255, 255))
            bw, bh = badge_surf.get_width() + 14, badge_surf.get_height() + 4
            bpill = pygame.Surface((bw, bh), pygame.SRCALPHA)
            pygame.draw.rect(bpill, (255, 45, 85, 230), (0, 0, bw, bh), border_radius=8)
            surface.blit(bpill, (cx - bw // 2, cy - r - bh // 2 + 2))
            surface.blit(badge_surf, (cx - badge_surf.get_width() // 2, cy - r - bh // 2 + 4))


class MenuScreen:
    """
    Premium Cyber Fruit Ninja Landing Page.
    Features:
    - Circular interactive target buttons for START, BLADE, MULTIPLAYER
    - Ambient glowing particles
    - background-landing.jpg backdrop
    """
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.title_font = pygame.font.SysFont("Arial", 56, bold=True)
        self.btn_title_font = pygame.font.SysFont("Arial", 22, bold=True)
        self.btn_sub_font = pygame.font.SysFont("Arial", 16, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 13)
        self.modal_font = pygame.font.SysFont("Arial", 24)

        # Ambient floating particle orbs
        self.orbs = [AmbientOrb(width, height) for _ in range(25)]

        # Load background-landing.jpg
        self.bg_image = None
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        bg_path = os.path.join(base_dir, "assets", "images", "background-landing.jpg")
        if os.path.exists(bg_path):
            try:
                raw_bg = pygame.image.load(bg_path).convert()
                self.bg_image = pygame.transform.scale(raw_bg, (width, height))
            except Exception as e:
                print(f"[Warning] Failed to load landing background: {e}")

        # Setup Circular Buttons
        btn_radius = 88
        cy = height // 2 + 85
        spacing = 290
        center_x = width // 2

        self.buttons = [
            CircleMenuButton("start", "START", "CLASSIC SOLO", center_x - spacing, cy, radius=btn_radius, theme_color=(30, 125, 225)),
            CircleMenuButton("blade", "BLADE", "CUSTOMIZE", center_x, cy, radius=btn_radius, theme_color=(235, 75, 45)),
            CircleMenuButton("multiplayer", "VS MODE", "MULTIPLAYER", center_x + spacing, cy, radius=btn_radius, theme_color=(235, 170, 35), badge="2-PLAYER")
        ]

        self.info_modal = None
        self.modal_timer = 0.0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for btn in self.buttons:
                if btn.collide_point((mx, my)):
                    return self._trigger_action(btn.action_id)

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_1, pygame.K_s):
                return "start"
            elif event.key in (pygame.K_2, pygame.K_b):
                return "blade"
            elif event.key in (pygame.K_3, pygame.K_m):
                return self._trigger_action("multiplayer")
            elif event.key == pygame.K_ESCAPE and self.info_modal:
                self.info_modal = None

        return None

    def _trigger_action(self, action_id):
        if action_id == "multiplayer":
            self.info_modal = "MULTIPLAYER 2-PLAYER CO-OP\nDual Hand Tracking / Split Screen Coming Soon!"
            self.modal_timer = 2.5
            return None
        return action_id

    def update(self, pos, blade_speed, dt):
        for orb in self.orbs:
            orb.update(dt)

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
        # 1. Background image
        if self.bg_image:
            surface.blit(self.bg_image, (0, 0))
        else:
            surface.fill((16, 18, 28))

        # 2. Ambient Orbs
        for orb in self.orbs:
            orb.draw(surface)

        # 3. Circular Buttons
        for btn in self.buttons:
            btn.draw(surface, self.btn_title_font, self.btn_sub_font, self.small_font)

        # 4. Bottom Navigation Hint
        foot_txt = self.small_font.render("Use your index finger to slice any circle  |  Keys: [1] Start  [2] Blade  [3] Multiplayer", True, (160, 175, 195))
        surface.blit(foot_txt, (self.width // 2 - foot_txt.get_width() // 2, self.height - 35))

        # 5. Modal
        if self.info_modal:
            modal_rect = pygame.Rect(self.width // 2 - 270, self.height // 2 - 80, 540, 160)
            modal_surf = pygame.Surface((modal_rect.width, modal_rect.height), pygame.SRCALPHA)
            modal_surf.fill((15, 20, 35, 245))
            pygame.draw.rect(modal_surf, (255, 65, 130), (0, 0, modal_rect.width, modal_rect.height), 3, border_radius=20)
            surface.blit(modal_surf, (modal_rect.x, modal_rect.y))

            lines = self.info_modal.split("\n")
            for i, line in enumerate(lines):
                c = (255, 255, 255) if i == 0 else (200, 220, 245)
                txt = self.modal_font.render(line, True, c)
                surface.blit(txt, (modal_rect.centerx - txt.get_width() // 2, modal_rect.y + 40 + i * 40))
