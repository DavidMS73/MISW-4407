from dataclasses import dataclass
from typing import Dict, List

import pygame


@dataclass
class EnemyTypeData:
	image: pygame.image
	velocity_min: float
	velocity_max: float


@dataclass
class SpawnEvent:
	time: float
	enemy_type: str
	position: pygame.Vector2
	spawned: bool = False


class CEnemySpawner:
	def __init__(self, spawn_events: List[SpawnEvent], enemy_types: Dict[str, EnemyTypeData]):
		self.spawn_events = spawn_events
		self.enemy_types = enemy_types
		self.elapsed_time = 0.0