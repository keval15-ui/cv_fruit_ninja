import pygame
import random
import math
import os

class JuiceParticle:
    """
    Represents a single splash/juice droplet released when a fruit is sliced.
    Handles movement, gravity, alpha fading, and rendering.
    """
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.radius = random.randint(3, 7)
        
        # Radial particle explosion math
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(4, 14)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.gravity = 0.3
        self.alpha = 255
        self.fade_rate = random.randint(6, 12)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.alpha -= self.fade_rate

    def is_alive(self):
        return self.alpha > 0

    def draw(self, surface):
        if self.alpha > 0:
            s = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            r, g, b = self.color[:3]
            pygame.draw.circle(s, (r, g, b, max(0, self.alpha)), (self.radius, self.radius), self.radius)
            surface.blit(s, (self.x - self.radius, self.y - self.radius))


class SlicedHalf:
    """
    Represents half of a sliced fruit spinning and flying off-screen.
    Inherits original fruit position/velocity plus an outward ejection force.
    """
    def __init__(self, image_or_color, x, y, vx, vy, radius, is_left_half=True, is_bomb=False):
        self.x = x
        self.y = y
        self.radius = radius
        self.is_left_half = is_left_half
        self.is_bomb = is_bomb

        # Ejection velocity: left half flies left, right half flies right
        boost_x = random.uniform(-6, -3) if is_left_half else random.uniform(3, 6)
        self.vx = vx + boost_x
        self.vy = vy + random.uniform(-3, 1)
        self.gravity = 0.5
        
        self.angle = 0
        self.rot_speed = random.uniform(6, 14) * (1.5 if is_left_half else -1.5)

        # Image or procedural fallback surface setup
        if isinstance(image_or_color, pygame.Surface):
            self.original_image = image_or_color
            self.color = None
        else:
            self.original_image = None
            self.color = image_or_color
            self.surf = self._create_procedural_half()

    def _create_procedural_half(self):
        """Creates a semi-circle surface if PNG image assets are not loaded."""
        surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        color = self.color if self.color else (200, 200, 200)
        
        # Draw semi-circle shape depending on left vs right half
        if self.is_left_half:
            pygame.draw.circle(surf, color, (self.radius, self.radius), self.radius)
            pygame.draw.rect(surf, (0, 0, 0, 0), (self.radius, 0, self.radius, self.radius * 2))
        else:
            pygame.draw.circle(surf, color, (self.radius, self.radius), self.radius)
            pygame.draw.rect(surf, (0, 0, 0, 0), (0, 0, self.radius, self.radius * 2))
            
        return surf

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.angle += self.rot_speed

    def draw(self, surface):
        img_to_rotate = self.original_image if self.original_image else self.surf
        rotated_img = pygame.transform.rotate(img_to_rotate, self.angle)
        rect = rotated_img.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(rotated_img, rect.topleft)


class Fruit:
    """
    Main Fruit / Bomb object that launches upward from below the screen.
    Handles continuous rotational momentum, trajectory updates, and splitting logic.
    """
    FRUIT_TYPES = {
        "watermelon": {"color": (76, 175, 80), "juice": (233, 30, 99), "radius": 45},
        "apple":      {"color": (229, 57, 53), "juice": (255, 205, 210), "radius": 38},
        "banana":     {"color": (253, 216, 53), "juice": (255, 241, 118), "radius": 35},
        "orange":     {"color": (255, 152, 0), "juice": (255, 224, 178), "radius": 40},
    }

    def __init__(self, screen_width, screen_height, image_dict=None):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.is_bomb = random.random() < 0.15  # 15% bomb spawn rate
        if self.is_bomb:
            self.fruit_type = "bomb"
            self.color = (40, 40, 40)
            self.juice_color = (255, 87, 34)
            self.radius = 35
        else:
            self.fruit_type = random.choice(list(self.FRUIT_TYPES.keys()))
            info = self.FRUIT_TYPES[self.fruit_type]
            self.color = info["color"]
            self.juice_color = info["juice"]
            self.radius = info["radius"]

        # Initial Position & Physics (Launch from bottom)
        self.x = random.randint(120, screen_width - 120)
        self.y = screen_height + 40
        
        self.vx = random.uniform(-4.5, 4.5)
        self.vy = random.uniform(-23.0, -17.0)
        self.gravity = 0.48
        
        # Rotational momentum
        self.angle = 0
        self.rot_speed = random.uniform(-8.0, 8.0)
        
        self.sliced = False
        self.image_dict = image_dict or {}
        self._load_sprites()

    def _load_sprites(self):
        """Loads sprite images if present in image_dict, else builds clean fallback textures."""
        self.sprite = self.image_dict.get(self.fruit_type)
        self.left_half_sprite = self.image_dict.get(f"{self.fruit_type}_left")
        self.right_half_sprite = self.image_dict.get(f"{self.fruit_type}_right")

        if not self.sprite:
            # Create fallback surface if PNG image asset is missing
            self.sprite = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            if self.is_bomb:
                # Render Bomb Texture
                pygame.draw.circle(self.sprite, (40, 40, 40), (self.radius, self.radius), self.radius)
                pygame.draw.circle(self.sprite, (220, 50, 50), (self.radius, self.radius), 10)
                pygame.draw.circle(self.sprite, (255, 235, 59), (self.radius + 10, self.radius - 10), 4)
            else:
                # Render Fruit Texture with specular highlight
                pygame.draw.circle(self.sprite, self.color, (self.radius, self.radius), self.radius)
                pygame.draw.circle(self.sprite, (255, 255, 255, 120), (self.radius - 8, self.radius - 8), self.radius // 4)

    def update(self):
        """Updates kinematic position and rotation."""
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.angle += self.rot_speed

    def draw(self, surface):
        """Renders the whole fruit with rotational angle."""
        if self.sliced:
            return

        rotated_img = pygame.transform.rotate(self.sprite, self.angle)
        rect = rotated_img.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(rotated_img, rect.topleft)

    def slice(self):
        """
        Triggers slice event. 
        Returns a tuple of (list_of_sliced_halves, list_of_juice_particles).
        """
        self.sliced = True
        halves = []
        particles = []

        # 1. Generate Juice Splash Particles
        particle_count = random.randint(20, 35) if not self.is_bomb else random.randint(35, 50)
        for _ in range(particle_count):
            p_color = self.juice_color if not self.is_bomb else (255, 100, 0)
            particles.append(JuiceParticle(self.x, self.y, p_color))

        # 2. Generate Split Halves (if it's a fruit)
        if not self.is_bomb:
            left_img = self.left_half_sprite if self.left_half_sprite else self.color
            right_img = self.right_half_sprite if self.right_half_sprite else self.color

            left_half = SlicedHalf(left_img, self.x - 10, self.y, self.vx, self.vy, self.radius, is_left_half=True)
            right_half = SlicedHalf(right_img, self.x + 10, self.y, self.vx, self.vy, self.radius, is_left_half=False)
            halves.extend([left_half, right_half])

        return halves, particles