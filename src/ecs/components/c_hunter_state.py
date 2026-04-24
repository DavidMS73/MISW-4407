from dataclasses import dataclass
from enum import Enum

import pygame


class HunterMode(Enum):
    IDLE = 0
    CHASE = 1
    RETURN = 2


@dataclass
class CHunterState:
    spawn_pos: pygame.Vector2
    velocity_chase: float
    velocity_return: float
    distance_start_chase: float
    distance_start_return: float
    mode: HunterMode = HunterMode.IDLE
    sound_chase: str | None = None
