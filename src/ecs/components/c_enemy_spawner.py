from dataclasses import dataclass
from typing import Dict, List

import pygame


@dataclass
class EnemyTypeData:
    image: pygame.image
    velocity_min: float
    velocity_max: float
    animations: dict | None = None
    velocity_chase: float | None = None
    velocity_return: float | None = None
    distance_start_chase: float | None = None
    distance_start_return: float | None = None
    sound: str | None = None
    sound_chase: str | None = None


@dataclass
class SpawnEvent:
    time: float
    enemy_type: str
    position: pygame.Vector2
    spawned: bool = False


class CEnemySpawner:
    def __init__(
        self, spawn_events: List[SpawnEvent], enemy_types: Dict[str, EnemyTypeData]
    ):
        self.spawn_events = spawn_events
        self.enemy_types = enemy_types
        self.elapsed_time = 0.0
