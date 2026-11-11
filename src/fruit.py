import pygame
import random
import math

class Particle:
    """Juice splash particle created upon slicing a fruit."""
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-5.0, 5.0)
        self.vy = random.uniform(-5.0, 5.0)
        self.radius = random.randint(3, 7)
        self.alpha = 255
        self.decay = random.randint(10, 18)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.alpha = max(0, self.alpha - self.decay)

    def is_alive(self):
        return self.alpha > 0

    def draw(self, surface):
        if self.alpha > 0:
            s = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color[:3], self.alpha), (self.radius, self.radius), self.radius)
            surface.blit(s, (int(self.x - self.radius), int(self.y - self.radius)))


class FruitHalf:
    """Flying half-piece of a sliced fruit separating along trajectory lines."""
    def __init__(self, x, y, radius, color, inner_color, is_left, angle):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.inner_color = inner_color
        self.is_left = is_left
        self.vx = -4.0 if is_left else 4.0
        self.vy = random.uniform(-7.0, -3.0)
        self.gravity = 0.4
        self.angle = angle
        self.rot_speed = -6.0 if is_left else 6.0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.angle += self.rot_speed

    def draw(self, surface):
        size = self.radius * 2 + 10
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2

        # Outer skin semicircle
        rect = pygame.Rect(cx - self.radius, cy - self.radius, self.radius * 2, self.radius * 2)
        start_angle = math.pi / 2 if self.is_left else -math.pi / 2
        end_angle = 3 * math.pi / 2 if self.is_left else math.pi / 2
        
        pygame.draw.circle(surf, self.color, (cx, cy), self.radius)
        pygame.draw.circle(surf, self.inner_color, (cx, cy), int(self.radius * 0.75))
        
        # Clip half to create split face
        clip_x = cx if self.is_left else cx - self.radius - 5
        clip_rect = pygame.Rect(clip_x, cy - self.radius - 5, self.radius + 5, self.radius * 2 + 10)
        surf.fill((0, 0, 0, 0), clip_rect)

        rotated_surf = pygame.transform.rotate(surf, self.angle)
        new_rect = rotated_surf.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(rotated_surf, new_rect.topleft)


class Fruit:
    """
    Spawns Watermelons, Apples, Bananas, Oranges, or Bombs (15% chance).
    Handles upward velocity physics, rotational movement, and slice splitting.
    """
    TYPES = {
        'watermelon': {'color': (40, 180, 50), 'inner': (230, 40, 40), 'radius': 45},
        'apple':      {'color': (220, 30, 30), 'inner': (245, 235, 190), 'radius': 36},
        'banana':     {'color': (240, 220, 40), 'inner': (255, 250, 210), 'radius': 30},
        'orange':     {'color': (255, 140, 0), 'inner': (255, 190, 60), 'radius': 38},
    }

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Easier mode uses fewer bombs.
        self.is_bomb = random.random() < 0.08

        if self.is_bomb:
            self.type = 'bomb'
            self.color = (35, 35, 35)
            self.juice_color = (255, 70, 0)
            self.radius = 34
        else:
            self.type = random.choice(list(self.TYPES.keys()))
            info = self.TYPES[self.type]
            self.color = info['color']
            self.juice_color = info['inner']
            self.radius = info['radius']

        self.x = random.randint(150, screen_width - 150)
        self.y = screen_height + self.radius
        self.vx = random.uniform(-2.5, 2.5)
        self.vy = random.uniform(-18.0, -15.0)  # Reach higher while staying manageable
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
        halves = [
            FruitHalf(self.x, self.y, self.radius, self.color, self.juice_color, True, self.angle),
            FruitHalf(self.x, self.y, self.radius, self.color, self.juice_color, False, self.angle)
        ]
        particles = [Particle(self.x, self.y, self.juice_color) for _ in range(18)]
        return halves, particles

    def draw(self, surface):
        if self.sliced:
            return

        size = self.radius * 2 + 14
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2

        if self.is_bomb:
            # Black metallic bomb body & fuse spark
            pygame.draw.circle(surf, (30, 30, 30), (cx, cy), self.radius)
            pygame.draw.circle(surf, (90, 90, 90), (cx - 8, cy - 8), self.radius // 3)
            pygame.draw.line(surf, (180, 140, 90), (cx, cy - self.radius), (cx + 10, cy - self.radius - 12), 4)
            pygame.draw.circle(surf, (255, 200, 0), (cx + 10, cy - self.radius - 12), 5)
            pygame.draw.circle(surf, (255, 50, 0), (cx + 10, cy - self.radius - 12), 2)
        else:
            # Procedural fruit body with inner flesh shading
            pygame.draw.circle(surf, self.color, (cx, cy), self.radius)
            pygame.draw.circle(surf, self.juice_color, (cx - 4, cy - 4), self.radius // 3)

        rotated_surf = pygame.transform.rotate(surf, self.angle)
        rect = rotated_surf.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(rotated_surf, rect.topleft)