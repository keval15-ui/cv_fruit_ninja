import pygame
from src.hand_tracker import HandTracker
from src.fruit import Fruit
from src.blade import Blade
from src.calibration import CalibrationScanner
from src.game_manager import GameManager

def main():
    pygame.init()
    WIDTH, HEIGHT = 1000, 700
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("CV Fruit Ninja - Finger Lock Edition")
    clock = pygame.time.Clock()

    # Initialize Modules
    tracker = HandTracker(WIDTH, HEIGHT, smooth_factor=0.6)
    blade = Blade(max_points=12)
    scanner = CalibrationScanner(WIDTH, HEIGHT, target_radius=65, hold_duration=1.5)
    manager = GameManager(WIDTH, HEIGHT)

    fruits = []
    sliced_halves = []
    particles = []
    spawn_timer = 0

    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds

        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and manager.game_over:
                if event.key == pygame.K_r:
                    scanner.reset()
                    manager.reset()
                    fruits.clear()
                    sliced_halves.clear()
                    particles.clear()

        # 2. Extract Fingertip Coordinate from Webcam
        pos, _ = tracker.get_fingertip_position(show_preview=True)
        blade.update(pos)

        # 3. Clear Screen
        screen.fill((15, 15, 25))

        # --- PHASE A: PRE-GAME CALIBRATION ---
        if not scanner.is_complete:
            scanner.update(pos, dt)

        # --- PHASE B: ACTIVE GAMEPLAY ---
        elif not manager.game_over:
            spawn_timer += 1
            if spawn_timer > 40:
                fruits.append(Fruit(WIDTH, HEIGHT))
                spawn_timer = 0

            blade_speed = blade.get_speed()

            for fruit in fruits[:]:
                fruit.update()
                fruit.draw(screen)

                # Slice collision check
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

                # Missed fruit check
                if fruit.y > HEIGHT + 60:
                    if not fruit.sliced and not fruit.is_bomb:
                        manager.lose_life()
                    fruits.remove(fruit)

        # 4. Render Flying Halves & Particles
        for half in sliced_halves[:]:
            half.update()
            half.draw(screen)
            if half.y > HEIGHT + 80:
                sliced_halves.remove(half)

        for p in particles[:]:
            p.update()
            p.draw(screen)
            if not p.is_alive():
                particles.remove(p)

        # 5. Render Blade Trail, UI, & Scanner Overlay
        blade.draw(screen)
        manager.update()
        manager.draw_ui(screen)
        scanner.draw(screen)  # Overlays the target scanner until complete

        pygame.display.flip()

    tracker.release()
    pygame.quit()

if __name__ == "__main__":
    main()