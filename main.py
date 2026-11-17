import os
import pygame
from src.hand_tracker import HandTracker
from src.blade import Blade
from src.screens import (
    LoadingScreen,
    CalibrationScreen,
    MenuScreen,
    CustomizationScreen,
    GameScreen
)

def main():
    pygame.init()
    WIDTH, HEIGHT = 1000, 700
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("CV Fruit Ninja - Motion Edition")
    clock = pygame.time.Clock()

    # Initialize Core Systems
    tracker = HandTracker(WIDTH, HEIGHT, margin=0.08)
    blade = Blade(max_points=12)

    # Initialize Screen Controllers
    loading_screen = LoadingScreen(WIDTH, HEIGHT, duration=1.2)
    calibration_screen = CalibrationScreen(WIDTH, HEIGHT, target_radius=65, hold_duration=1.5)
    menu_screen = MenuScreen(WIDTH, HEIGHT)
    customization_screen = CustomizationScreen(WIDTH, HEIGHT)
    game_screen = GameScreen(WIDTH, HEIGHT)

    intro_music_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "assets",
        "sounds",
        "Fruit Ninja.mp3",
    )
    intro_music_loaded = False
    try:
        pygame.mixer.music.load(intro_music_path)
        intro_music_loaded = True
    except pygame.error as error:
        print(f"[Warning] Failed to load intro music: {error}")

    def sync_intro_music():
        """Play the intro music only while outside the gameplay screen."""
        should_play = current_state != "game"
        if not intro_music_loaded:
            return

        if should_play:
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.play(-1)
        else:
            pygame.mixer.music.stop()

    # Initial Screen State
    current_state = "loading"  # "loading" -> "calibration" -> "menu" -> ("game" | "customization")

    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds

        # 1. Fingertip Extraction
        pos, _ = tracker.get_fingertip_position(show_preview=True)
        blade.update(pos)
        blade_speed = blade.get_speed()

        # 2. Event Handling & State Machine Transitions
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if current_state == "loading":
                loading_screen.handle_event(event)

            elif current_state == "calibration":
                calibration_screen.handle_event(event)

            elif current_state == "menu":
                action = menu_screen.handle_event(event)
                if action in ("classic", "time_attack", "zen", "survival"):
                    game_screen.reset(action)
                    current_state = "game"
                elif action == "blade":
                    current_state = "customization"

            elif current_state == "customization":
                action = customization_screen.handle_event(event)
                if action == "back":
                    outer, inner = customization_screen.get_selected_blade_colors()
                    blade.set_palette(outer, inner)
                    current_state = "menu"

            elif current_state == "game":
                action = game_screen.handle_event(event)
                if action == "menu":
                    current_state = "menu"

        # 3. State Updates
        if current_state == "loading":
            loading_screen.update(dt)
            if loading_screen.is_finished:
                current_state = "calibration"

        elif current_state == "calibration":
            if calibration_screen.update(pos, dt):
                current_state = "menu"

        elif current_state == "menu":
            action = menu_screen.update(pos, blade_speed, dt)
            if action in ("classic", "time_attack", "zen", "survival"):
                game_screen.reset(action)
                current_state = "game"
            elif action == "blade":
                current_state = "customization"

        elif current_state == "customization":
            action = customization_screen.update(pos, blade_speed, dt)
            if action == "back":
                outer, inner = customization_screen.get_selected_blade_colors()
                blade.set_palette(outer, inner)
                current_state = "menu"

        elif current_state == "game":
            game_screen.update(blade, dt)

        sync_intro_music()

        # 4. Rendering
        if current_state == "loading":
            loading_screen.draw(screen)

        elif current_state == "calibration":
            calibration_screen.draw(screen)

        elif current_state == "menu":
            menu_screen.draw(screen)

        elif current_state == "customization":
            customization_screen.draw(screen)

        elif current_state == "game":
            game_screen.draw(screen)

        # Draw glowing blade trail across screens (except initial loading screen)
        if current_state != "loading":
            blade.draw(screen)

        pygame.display.flip()

    tracker.release()
    pygame.mixer.music.stop()
    pygame.quit()

if __name__ == "__main__":
    main()