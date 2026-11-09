import pygame
import math

class Blade:
    """
    Tracks historical fingertip positions, calculates slice velocity,
    and renders a glowing neon blade trail.
    """
    def __init__(self, max_points=12, outer_color=(0, 240, 255), inner_color=(255, 255, 255)):
        self.blade_pts = []
        self.max_points = max_points
        self.outer_color = outer_color
        self.inner_color = inner_color

    def update(self, current_pos):
        """Appends current fingertip position and maintains point buffer queue."""
        if current_pos is not None:
            self.blade_pts.append(current_pos)
            if len(self.blade_pts) > self.max_points:
                self.blade_pts.pop(0)
        else:
            self.blade_pts.clear()

    def get_speed(self):
        """Calculates instantaneous speed based on distance between the two newest points."""
        if len(self.blade_pts) < 2:
            return 0.0
        p1 = self.blade_pts[-1]
        p2 = self.blade_pts[-2]
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

    def get_tip(self):
        """Returns the current fingertip coordinate."""
        return self.blade_pts[-1] if self.blade_pts else None

    def draw(self, surface):
        """Draws multi-layered alpha blade trail with additive glow blending."""
        if len(self.blade_pts) < 2:
            return

        trail_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        num_pts = len(self.blade_pts)

        for i in range(1, num_pts):
            progress = i / num_pts  # 0.0 (oldest) to 1.0 (newest tip)
            outer_width = int(progress * 16)
            inner_width = int(progress * 6)
            alpha = int(progress * 255)

            p1 = self.blade_pts[i - 1]
            p2 = self.blade_pts[i]

            if outer_width > 0:
                # Outer cyan aura
                pygame.draw.line(trail_surface, (*self.outer_color, alpha // 2), p1, p2, outer_width)
                # Inner white hot core
                pygame.draw.line(trail_surface, (*self.inner_color, alpha), p1, p2, inner_width)

        # Apply Additive Blending (BLEND_ADD) to create light glow
        surface.blit(trail_surface, (0, 0), special_flags=pygame.BLEND_ADD)