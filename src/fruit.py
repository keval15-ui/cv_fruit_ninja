import pygame
import random
import math


# ---------------------------------------------------------------------------
# Fruit type definitions
# ---------------------------------------------------------------------------
# Each entry:
#   color        – outer skin color
#   inner        – inner flesh color
#   juice_color  – particle splash color
#   radius       – spawn radius (px)
#   vy_range     – (min, max) initial upward velocity  (negative = up)
#   weight       – relative spawn weight

TYPES = {
    'watermelon': {
        'color':       (30, 140, 40),
        'inner':       (220, 35, 50),
        'juice_color': (210, 20, 40),
        'radius':      46,
        'vy_range':    (-14, -12),
        'weight':      1,
    },
    'mango': {
        'color':       (240, 185, 30),
        'inner':       (255, 235, 130),
        'juice_color': (240, 140, 20),
        'radius':      38,
        'vy_range':    (-18, -15),
        'weight':      2,
    },
    'apple': {
        'color':       (210, 25, 25),
        'inner':       (245, 240, 200),
        'juice_color': (230, 230, 180),
        'radius':      36,
        'vy_range':    (-18, -15),
        'weight':      3,
    },
    'orange': {
        'color':       (245, 135, 20),
        'inner':       (255, 195, 90),
        'juice_color': (255, 170, 30),
        'radius':      38,
        'vy_range':    (-18, -15),
        'weight':      3,
    },
    'guava': {
        'color':       (185, 215, 110),
        'inner':       (240, 140, 160),
        'juice_color': (230, 110, 150),
        'radius':      35,
        'vy_range':    (-18, -15),
        'weight':      2,
    },
    'banana': {
        'color':       (250, 225, 30),
        'inner':       (255, 250, 210),
        'juice_color': (240, 230, 170),
        'radius':      28,
        'vy_range':    (-18, -15),
        'weight':      2,
    },
    'cherry': {
        'color':       (170, 15, 30),
        'inner':       (240, 160, 170),
        'juice_color': (160, 10, 25),
        'radius':      22,
        'vy_range':    (-22, -18),
        'weight':      3,
    },
}

# Build weighted spawn list once
_SPAWN_POOL: list[str] = []
for _name, _info in TYPES.items():
    _SPAWN_POOL.extend([_name] * _info['weight'])


# ---------------------------------------------------------------------------
# Helper: lighten a colour
# ---------------------------------------------------------------------------

def _lighten(color, amount=60):
    return tuple(min(255, c + amount) for c in color[:3])


def _darken(color, amount=40):
    return tuple(max(0, c - amount) for c in color[:3])


# ---------------------------------------------------------------------------
# Fruit-specific drawing helpers (whole fruit, outer skin)
# ---------------------------------------------------------------------------

def _draw_whole_fruit(surf: pygame.Surface, cx: int, cy: int,
                      fruit_type: str, color: tuple, radius: int) -> None:
    """Draw the outer skin of an unsliced fruit onto *surf*."""

    if fruit_type == 'watermelon':
        # Dark-green base
        pygame.draw.circle(surf, (25, 120, 30), (cx, cy), radius)
        # Lighter green stripes (3 curved stripes simulated as thin ellipses)
        stripe_col = (80, 185, 60)
        for angle_deg in (-40, 0, 40):
            ang = math.radians(angle_deg)
            sx = int(cx + math.sin(ang) * radius * 0.5)
            sy = int(cy - math.cos(ang) * radius * 0.5)
            stripe_w = max(4, radius // 6)
            stripe_h = int(radius * 1.6)
            r = pygame.Rect(sx - stripe_w // 2, sy - stripe_h // 2,
                            stripe_w, stripe_h)
            pygame.draw.ellipse(surf, stripe_col, r)
        # Re-clip to circle boundary
        pygame.draw.circle(surf, (25, 120, 30), (cx, cy), radius, 0)
        # Redraw stripes clipped by using a mask approach: just overdraw border
        for angle_deg in (-40, 0, 40):
            ang = math.radians(angle_deg)
            sx = int(cx + math.sin(ang) * radius * 0.5)
            sy = int(cy - math.cos(ang) * radius * 0.5)
            stripe_w = max(3, radius // 7)
            stripe_h = int(radius * 1.6)
            r = pygame.Rect(sx - stripe_w // 2, sy - stripe_h // 2,
                            stripe_w, stripe_h)
            pygame.draw.ellipse(surf, (90, 200, 70), r)
        # Dark border ring
        pygame.draw.circle(surf, (20, 100, 25), (cx, cy), radius, 3)

    elif fruit_type == 'mango':
        # Golden-yellow base
        pygame.draw.circle(surf, (240, 185, 30), (cx, cy), radius)
        # Orange blush on one side
        blush_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        for r_step in range(radius, 0, -4):
            alpha = int(80 * (1 - r_step / radius))
            pygame.draw.circle(blush_surf, (255, 110, 10, alpha),
                               (radius + radius // 3, radius - radius // 4), r_step)
        surf.blit(blush_surf, (cx - radius, cy - radius))
        # Highlight
        pygame.draw.ellipse(surf, (255, 235, 140),
                            (cx - radius // 2, cy - radius // 2,
                             radius // 2, radius // 3))

    elif fruit_type == 'apple':
        # Vivid red body
        pygame.draw.circle(surf, (210, 25, 25), (cx, cy), radius)
        # Darker red on bottom-right for depth
        pygame.draw.circle(surf, (170, 10, 10),
                           (cx + radius // 4, cy + radius // 4), radius // 2)
        # Light highlight top-left
        pygame.draw.ellipse(surf, (255, 120, 120),
                            (cx - radius // 2, cy - radius // 2,
                             radius // 2, radius // 3))
        pygame.draw.ellipse(surf, (255, 200, 200),
                            (cx - radius // 2 + 3, cy - radius // 2 + 3,
                             radius // 4, radius // 6))
        # Brown stem
        stem_x = cx
        stem_y = cy - radius
        pygame.draw.line(surf, (100, 60, 20),
                         (stem_x, stem_y), (stem_x + 4, stem_y - 10), 3)
        # Small leaf hint
        pygame.draw.ellipse(surf, (60, 160, 40),
                            (stem_x + 2, stem_y - 12, 8, 5))

    elif fruit_type == 'orange':
        # Orange dimpled skin base
        pygame.draw.circle(surf, (245, 135, 20), (cx, cy), radius)
        # Peel texture: tiny dark dots over the surface
        peel_col = (220, 110, 10)
        random.seed(42)
        for _ in range(22):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(0.2, 0.85) * radius
            px = int(cx + math.cos(angle) * dist)
            py = int(cy + math.sin(angle) * dist)
            pygame.draw.circle(surf, peel_col, (px, py), 2)
        random.seed()
        # Highlight
        pygame.draw.ellipse(surf, (255, 190, 100),
                            (cx - radius // 2, cy - radius // 2,
                             radius // 2, radius // 3))

    elif fruit_type == 'guava':
        # Pale yellow-green base
        pygame.draw.circle(surf, (185, 215, 110), (cx, cy), radius)
        # Slightly darker green ring
        pygame.draw.circle(surf, (155, 190, 85), (cx, cy), radius, 3)
        # Highlight
        pygame.draw.ellipse(surf, (220, 240, 160),
                            (cx - radius // 2, cy - radius // 2,
                             radius // 2, radius // 3))
        # Small nub at bottom (guava tip)
        pygame.draw.circle(surf, (140, 175, 75),
                           (cx, cy + radius - 6), 5)

    elif fruit_type == 'banana':
        # Bright yellow ellipse (simulate curved banana body)
        pygame.draw.ellipse(surf, (250, 225, 30),
                            (cx - radius, cy - int(radius * 0.65),
                             radius * 2, int(radius * 1.3)))
        # Darker yellow shadow on bottom
        pygame.draw.ellipse(surf, (210, 180, 10),
                            (cx - radius + 4, cy + radius // 4,
                             int(radius * 1.6), int(radius * 0.5)))
        # Highlight strip
        pygame.draw.ellipse(surf, (255, 250, 170),
                            (cx - radius // 2, cy - radius // 2,
                             radius // 3, int(radius * 0.8)))
        # Tip nubs
        pygame.draw.circle(surf, (180, 140, 20),
                           (cx - radius + 2, cy), 4)
        pygame.draw.circle(surf, (180, 140, 20),
                           (cx + radius - 2, cy), 4)

    elif fruit_type == 'cherry':
        # Deep red body
        pygame.draw.circle(surf, (170, 15, 30), (cx, cy), radius)
        # Lighter red highlight
        pygame.draw.ellipse(surf, (230, 80, 90),
                            (cx - radius // 2, cy - radius // 2,
                             radius // 2, radius // 3))
        pygame.draw.ellipse(surf, (255, 160, 165),
                            (cx - radius // 2 + 2, cy - radius // 2 + 2,
                             radius // 4, radius // 5))
        # Green stem
        pygame.draw.line(surf, (40, 160, 40),
                         (cx, cy - radius),
                         (cx + 6, cy - radius - 14), 2)


# ---------------------------------------------------------------------------
# Inner flesh drawing helpers (for FruitHalf)
# ---------------------------------------------------------------------------

def _draw_inner_flesh(surf: pygame.Surface, cx: int, cy: int,
                      fruit_type: str, inner_color: tuple, radius: int) -> None:
    """Draw inner flesh details onto the half surface."""

    # Base flesh circle
    pygame.draw.circle(surf, inner_color, (cx, cy), int(radius * 0.78))

    if fruit_type == 'watermelon':
        # Slightly lighter center
        pygame.draw.circle(surf, _lighten(inner_color, 30),
                           (cx, cy), int(radius * 0.45))
        # Black seed dots
        seed_positions = [
            (-0.25, -0.3), (0.3, -0.1), (-0.1, 0.35),
            (0.25, 0.3),  (-0.4, 0.1),
        ]
        for sx_r, sy_r in seed_positions:
            px = int(cx + sx_r * radius * 0.7)
            py = int(cy + sy_r * radius * 0.7)
            pygame.draw.ellipse(surf, (20, 20, 20),
                                (px - 4, py - 6, 8, 12))

    elif fruit_type == 'orange':
        # 6 segment lines from center
        seg_col = (200, 130, 20)
        for i in range(6):
            angle = math.radians(i * 60)
            ex = int(cx + math.cos(angle) * radius * 0.75)
            ey = int(cy + math.sin(angle) * radius * 0.75)
            pygame.draw.line(surf, seg_col, (cx, cy), (ex, ey), 2)
        # Center nub
        pygame.draw.circle(surf, (220, 150, 30), (cx, cy), 5)

    elif fruit_type == 'guava':
        # Pink flesh with seed cluster in center
        pygame.draw.circle(surf, (250, 170, 185), (cx, cy), int(radius * 0.35))
        seed_col = (200, 90, 110)
        for i in range(8):
            angle = math.radians(i * 45)
            dist = radius * 0.22
            px = int(cx + math.cos(angle) * dist)
            py = int(cy + math.sin(angle) * dist)
            pygame.draw.circle(surf, seed_col, (px, py), 3)

    elif fruit_type == 'apple':
        # Cream with 5-point star core hint
        pygame.draw.circle(surf, _lighten(inner_color, 20), (cx, cy), int(radius * 0.4))
        # Core line hint
        pygame.draw.line(surf, (160, 120, 80),
                         (cx, cy - int(radius * 0.5)),
                         (cx, cy + int(radius * 0.5)), 2)

    elif fruit_type == 'mango':
        # Bright yellow centre
        pygame.draw.circle(surf, (255, 245, 100), (cx, cy), int(radius * 0.4))
        # Fibrous lines
        for i in range(5):
            angle = math.radians(i * 36 + 10)
            ex = int(cx + math.cos(angle) * radius * 0.65)
            ey = int(cy + math.sin(angle) * radius * 0.65)
            pygame.draw.line(surf, (220, 190, 60), (cx, cy), (ex, ey), 1)

    elif fruit_type == 'banana':
        # Cream flesh, darker oval seed dots
        pygame.draw.circle(surf, (255, 252, 230), (cx, cy), int(radius * 0.5))
        for i in range(3):
            angle = math.radians(i * 120)
            px = int(cx + math.cos(angle) * radius * 0.3)
            py = int(cy + math.sin(angle) * radius * 0.3)
            pygame.draw.circle(surf, (180, 160, 80), (px, py), 2)

    elif fruit_type == 'cherry':
        # Pale pink with centre dot
        pygame.draw.circle(surf, (255, 190, 200), (cx, cy), int(radius * 0.5))
        pygame.draw.circle(surf, (200, 100, 115), (cx, cy), 4)


# ===========================================================================
# Particle
# ===========================================================================

class Particle:
    """Juice splash particle created upon slicing a fruit."""

    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-6.0, 6.0)
        self.vy = random.uniform(-7.0, -1.0)
        self.gravity = 0.3
        self.radius = random.randint(3, 8)
        self.alpha = 255
        self.decay = random.randint(8, 16)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.alpha = max(0, self.alpha - self.decay)

    def is_alive(self):
        return self.alpha > 0

    def draw(self, surface):
        if self.alpha > 0:
            s = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color[:3], self.alpha),
                               (self.radius, self.radius), self.radius)
            surface.blit(s, (int(self.x - self.radius), int(self.y - self.radius)))


# ===========================================================================
# FruitHalf
# ===========================================================================

class FruitHalf:
    """Flying half-piece of a sliced fruit."""

    def __init__(self, x, y, radius, color, inner_color, is_left, angle,
                 fruit_type='watermelon'):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.inner_color = inner_color
        self.is_left = is_left
        self.vx = -4.5 if is_left else 4.5
        self.vy = random.uniform(-8.0, -3.0)
        self.gravity = 0.4
        self.angle = angle
        self.rot_speed = -7.0 if is_left else 7.0
        self.fruit_type = fruit_type

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.angle += self.rot_speed

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, val):
        self._y = val

    def draw(self, surface):
        size = self.radius * 2 + 16
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2

        # --- Draw full outer skin + inner flesh ---
        _draw_whole_fruit(surf, cx, cy, self.fruit_type, self.color, self.radius)
        _draw_inner_flesh(surf, cx, cy, self.fruit_type, self.inner_color, self.radius)

        # --- Clip away one half to create the cut face ---
        # Left half: keep left side, erase right  |  Right half: keep right, erase left
        if self.is_left:
            clip_rect = pygame.Rect(cx, cy - self.radius - 6,
                                    self.radius + 8, self.radius * 2 + 12)
        else:
            clip_rect = pygame.Rect(cx - self.radius - 8, cy - self.radius - 6,
                                    self.radius + 8, self.radius * 2 + 12)
        surf.fill((0, 0, 0, 0), clip_rect)

        # Thin cut-line highlight on the flat edge
        cut_x = cx
        pygame.draw.line(surf, (255, 255, 255, 180),
                         (cut_x, cy - self.radius),
                         (cut_x, cy + self.radius), 2)

        rotated_surf = pygame.transform.rotate(surf, self.angle)
        new_rect = rotated_surf.get_rect(center=(int(self.x), int(self._y)))
        surface.blit(rotated_surf, new_rect.topleft)


# ===========================================================================
# Fruit
# ===========================================================================

class Fruit:
    """
    Spawns fruits or Bombs (8% chance).
    Handles physics, rotation and slice splitting.
    """

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.is_bomb = random.random() < 0.08

        if self.is_bomb:
            self.type = 'bomb'
            self.color = (35, 35, 35)
            self.juice_color = (255, 70, 0)
            self.radius = 34
            vy_min, vy_max = -18, -15
        else:
            self.type = random.choice(_SPAWN_POOL)
            info = TYPES[self.type]
            self.color = info['color']
            self.juice_color = info['juice_color']
            self.radius = info['radius']
            vy_min, vy_max = info['vy_range']

        self.x = random.randint(150, screen_width - 150)
        self.y = screen_height + self.radius
        self.vx = random.uniform(-2.5, 2.5)
        self.vy = random.uniform(vy_min, vy_max)
        self.gravity = 0.38
        self.angle = 0.0
        self.rot_speed = random.uniform(-5.0, 5.0)
        self.sliced = False

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.angle += self.rot_speed

    def slice(self):
        self.sliced = True
        inner = TYPES[self.type]['inner'] if not self.is_bomb else self.juice_color
        halves = [
            FruitHalf(self.x, self.y, self.radius, self.color, inner,
                      True, self.angle, self.type),
            FruitHalf(self.x, self.y, self.radius, self.color, inner,
                      False, self.angle, self.type),
        ]
        particles = [Particle(self.x, self.y, self.juice_color) for _ in range(22)]
        return halves, particles

    def draw(self, surface):
        if self.sliced:
            return

        size = self.radius * 2 + 16
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2

        if self.is_bomb:
            # Metallic black bomb body
            pygame.draw.circle(surf, (30, 30, 30), (cx, cy), self.radius)
            # Rim highlight
            pygame.draw.circle(surf, (80, 80, 80), (cx, cy), self.radius, 3)
            # Shine spot
            pygame.draw.circle(surf, (100, 100, 100),
                               (cx - 9, cy - 9), self.radius // 3)
            pygame.draw.ellipse(surf, (160, 160, 160),
                                (cx - 13, cy - 13, 10, 7))
            # Fuse cord
            pygame.draw.line(surf, (160, 130, 80),
                             (cx, cy - self.radius),
                             (cx + 11, cy - self.radius - 13), 4)
            # Spark
            spark_x = cx + 11
            spark_y = cy - self.radius - 13
            pygame.draw.circle(surf, (255, 200, 0), (spark_x, spark_y), 6)
            pygame.draw.circle(surf, (255, 80, 0), (spark_x, spark_y), 3)
        else:
            _draw_whole_fruit(surf, cx, cy, self.type, self.color, self.radius)

        rotated_surf = pygame.transform.rotate(surf, self.angle)
        rect = rotated_surf.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(rotated_surf, rect.topleft)
