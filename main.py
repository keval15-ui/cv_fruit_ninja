import pygame
import random
from src.hand_tracker import HandTracker
from src.fruit import Fruit
from src.blade import Blade
from src.game_manager import GameManager

def main():
    pygame.init()
    WIDTH, HEIGHT = 1000, 700
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("CV Fruit Ninja AI")
    clock = pygame.time.Clock()

    # Initialize Modules (Optimized for low-latency fast gesture tracking)
    tracker = HandTracker(WIDTH, HEIGHT, smooth_factor=0.6)
    blade = Blade(max_points=12)
    manager = GameManager(WIDTH, HEIGHT)

    fruits = []
    sliced_halves = []
    particles = []
    spawn_timer = 0

    running = True
    while running:
        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and manager.game_over:
                if event.key == pygame.K_r:
                    manager.reset()
                    fruits.clear()
                    sliced_halves.clear()
                    particles.clear()

        # 2. Extract Smoothed Fingertip Position from Webcam
        pos, camera_frame = tracker.get_fingertip_position(show_preview=True)
        blade.update(pos)

        # 3. Clear Screen & Render Background
        screen.fill((15, 15, 25))

        if not manager.game_over:
            # Spawn Fruit Waves Periodically
            spawn_timer += 1
            if spawn_timer > 40:
                fruits.append(Fruit(WIDTH, HEIGHT))
                spawn_timer = 0

            blade_speed = blade.get_speed()

            # Update Active Fruits & Check Slices
            for fruit in fruits[:]:
                fruit.update()
                fruit.draw(screen)

                # Line-Segment Collision Check: Validates fast slashes between frames
                if not fruit.sliced and blade_speed > 8:
                    if blade.check_collision(fruit.x, fruit.y, fruit.radius):
                        halves, new_particles = fruit.slice()
                        sliced_halves.extend(halves)
                        particles.extend(new_particles)

                        if fruit.is_bomb:
                            manager.game_over = True
                        else:
                            manager.add_score(10, fruit.x, fruit.y)
                            manager.add_stain(fruit.x, fruit.y, fruit.juice_color)

                        fruits.remove(fruit)
                        continue

                # Missed Fruit Check (Fell below bottom screen border)
                if fruit.y > HEIGHT + 60:
                    if not fruit.sliced and not fruit.is_bomb:
                        manager.lose_life()
                    fruits.remove(fruit)

        # 4. Update & Draw Flying Sliced Fruit Halves
        for half in sliced_halves[:]:
            half.update()
            half.draw(screen)
            if half.y > HEIGHT + 80:
                sliced_halves.remove(half)

        # 5. Update & Draw Juice Particles
        for p in particles[:]:
            p.update()
            p.draw(screen)
            if not p.is_alive():
                particles.remove(p)

        # 6. Draw Glowing Blade Trail & UI Overlay
        blade.draw(screen)
        manager.update()
        manager.draw_ui(screen)

        pygame.display.flip()
        clock.tick(60)

    tracker.release()
    pygame.quit()

if __name__ == "__main__":
    main()