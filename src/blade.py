import pygame
import math

def check_line_circle_collision(p1, p2, circle_x, circle_y, radius):
   
    x1, y1 = p1
    x2, y2 = p2
    
    dx = x2 - x1
    dy = y2 - y1
    
    if dx == 0 and dy == 0:
        return math.hypot(circle_x - x1, circle_y - y1) < radius

    t = ((circle_x - x1) * dx + (circle_y - y1) * dy) / (dx * dx + dy * dy)
    t = max(0, min(1, t))

    nearest_x = x1 + t * dx
    nearest_y = y1 + t * dy

    distance = math.hypot(circle_x - nearest_x, circle_y - nearest_y)
    return distance < radius


class Blade:
    """
    Tracks historical fingertip positions, calculates slice velocity,
    renders a glowing neon blade trail, and handles slice collision math.
    Fades out the trail when the hand is stationary.
    """
    def __init__(self, max_points=12, outer_color=(0, 240, 255), inner_color=(255, 255, 255)):
        self.blade_pts = []
        self.max_points = max_points
        self.outer_color = outer_color
        self.inner_color = inner_color
        self.min_movement_dist = 6  # Minimum pixels moved to add a new trail point

    def update(self, current_pos):
        """
        Appends new position only when moving beyond deadzone threshold.
        Fades/decays the trail when the hand is held still or lost.
        """
        if current_pos is not None:
            if not self.blade_pts:
                self.blade_pts.append(current_pos)
            else:
                last_pt = self.blade_pts[-1]
                dist = math.hypot(current_pos[0] - last_pt[0], current_pos[1] - last_pt[1])
                
                if dist >= self.min_movement_dist:
                    self.blade_pts.append(current_pos)
                    if len(self.blade_pts) > self.max_points:
                        self.blade_pts.pop(0)
                else:
                    # Hand is stationary: decay old points so trail fades out
                    if self.blade_pts:
                        self.blade_pts.pop(0)
        else:
            # Hand tracking lost: decay points
            if self.blade_pts:
                self.blade_pts.pop(0)

    def get_speed(self):
        if len(self.blade_pts) < 2:
            return 0.0
        p1 = self.blade_pts[-1]
        p2 = self.blade_pts[-2]
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

    def get_tip(self):
        return self.blade_pts[-1] if self.blade_pts else None

    def check_collision(self, circle_x, circle_y, radius):
        if len(self.blade_pts) < 2:
            return False
        p1 = self.blade_pts[-1]
        p2 = self.blade_pts[-2]
        return check_line_circle_collision(p1, p2, circle_x, circle_y, radius)

    def draw(self, surface):
        if len(self.blade_pts) < 2:
            return

        trail_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        num_pts = len(self.blade_pts)

        for i in range(1, num_pts):
            progress = i / num_pts
            outer_width = int(progress * 16)
            inner_width = int(progress * 6)
            alpha = int(progress * 255)

            p1 = self.blade_pts[i - 1]
            p2 = self.blade_pts[i]

            if outer_width > 0:
                pygame.draw.line(trail_surface, (*self.outer_color, alpha // 2), p1, p2, outer_width)
                pygame.draw.line(trail_surface, (*self.inner_color, alpha), p1, p2, inner_width)

        surface.blit(trail_surface, (0, 0), special_flags=pygame.BLEND_ADD)