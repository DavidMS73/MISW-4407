import random

import esper
import pygame

from src.create.prefab_creator import crear_cuadrado
from src.ecs.components.c_enemy_spawner import CEnemySpawner, EnemyTypeData, SpawnEvent


def _build_spawn_velocity(enemy_type_data: EnemyTypeData) -> pygame.Vector2:
	speed = random.uniform(enemy_type_data.velocity_min, enemy_type_data.velocity_max)
	dir_x = random.choice((-1, 1))
	dir_y = random.choice((-1, 1))
	return pygame.Vector2(speed * dir_x, speed * dir_y)


def _spawn_enemy(world: esper.World, event: SpawnEvent, enemy_type_data: EnemyTypeData) -> None:
	crear_cuadrado(
		world,
		pos=pygame.Vector2(event.position.x, event.position.y),
		vel=_build_spawn_velocity(enemy_type_data),
		size=pygame.Vector2(enemy_type_data.size.x, enemy_type_data.size.y),
		color=pygame.Color(enemy_type_data.color.r, enemy_type_data.color.g, enemy_type_data.color.b),
	)


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
