import math
import random

import esper
import pygame

from src.create.prefab_creator import _spawn_enemy, create_square
from src.ecs.components.c_enemy_spawner import CEnemySpawner, EnemyTypeData, SpawnEvent
from src.ecs.components.tags.c_tag_enemy import CTagEnemy


def system_enemy_spawner(world: esper.World, delta_time: float) -> None:
    spawners = list(world.get_component(CEnemySpawner))
    if len(spawners) != 1:
        raise ValueError("Debe existir exactamente una entidad con CEnemySpawner")

    _, c_spawner = spawners[0]
    c_spawner.elapsed_time += delta_time

    for event in c_spawner.spawn_events:
        if event.spawned:
            continue

        if c_spawner.elapsed_time < event.time:
            continue

        enemy_type_data = c_spawner.enemy_types.get(event.enemy_type)
        if enemy_type_data is None:
            event.spawned = True
            continue

        _spawn_enemy(world, event, enemy_type_data)
        event.spawned = True
