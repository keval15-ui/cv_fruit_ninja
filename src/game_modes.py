from dataclasses import dataclass


@dataclass(frozen=True)
class GameMode:
    title: str
    duration: float
    lives: int
    allow_bombs: bool
    spawn_interval: int
    endless: bool = False


GAME_MODES = {
    "classic": GameMode(
        title="CLASSIC",
        duration=30.0,
        lives=5,
        allow_bombs=True,
        spawn_interval=55,
    ),
    "time_attack": GameMode(
        title="TIME ATTACK",
        duration=60.0,
        lives=3,
        allow_bombs=True,
        spawn_interval=42,
    ),
    "zen": GameMode(
        title="ZEN",
        duration=60.0,
        lives=5,
        allow_bombs=False,
        spawn_interval=45,
    ),
    "survival": GameMode(
        title="SURVIVAL",
        duration=0.0,
        lives=5,
        allow_bombs=True,
        spawn_interval=48,
        endless=True,
    ),
}
