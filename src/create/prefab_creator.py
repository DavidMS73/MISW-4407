import esper
import pygame

from src.ecs.components.c_enemy_spawner import CEnemySpawner, EnemyTypeData, SpawnEvent
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.tags.c_tag_player import CTagPlayer
from src.ecs.components.c_input_command import CInputCommand


def create_square(
    ecs_world: esper.World,
    pos: pygame.Vector2,
    vel: pygame.Vector2,
    size: pygame.Vector2,
    color: pygame.Color,
) -> int:
    cuad_entity = ecs_world.create_entity()
    ecs_world.add_component(cuad_entity, CSurface(size=size, color=color))
    ecs_world.add_component(cuad_entity, CTransform(pos=pos))
    ecs_world.add_component(cuad_entity, CVelocity(vel=vel))
    return cuad_entity


def _build_enemy_types(enemy_types_cfg: dict) -> dict[str, EnemyTypeData]:
    enemy_types: dict[str, EnemyTypeData] = {}
    for enemy_type, enemy_data in enemy_types_cfg.items():
        enemy_types[enemy_type] = EnemyTypeData(
            size=pygame.Vector2(enemy_data["size"]["x"], enemy_data["size"]["y"]),
            color=pygame.Color(
                enemy_data["color"]["r"],
                enemy_data["color"]["g"],
                enemy_data["color"]["b"],
            ),
            velocity_min=enemy_data["velocity_min"],
            velocity_max=enemy_data["velocity_max"],
        )
    return enemy_types


def _build_spawn_events(level_cfg: dict) -> list[SpawnEvent]:
    events: list[SpawnEvent] = []
    for event in level_cfg["enemy_spawn_events"]:
        events.append(
            SpawnEvent(
                time=event["time"],
                enemy_type=event["enemy_type"],
                position=pygame.Vector2(event["position"]["x"], event["position"]["y"]),
            )
        )
    events.sort(key=lambda spawn_event: spawn_event.time)
    return events


def create_enemy_spawner(
    ecs_world: esper.World, enemy_types_cfg: dict, level_cfg: dict
) -> None:
    spawner_entity = ecs_world.create_entity()
    c_enemy_spawner = CEnemySpawner(
        spawn_events=_build_spawn_events(level_cfg),
        enemy_types=_build_enemy_types(enemy_types_cfg),
    )
    ecs_world.add_component(spawner_entity, c_enemy_spawner)


def create_player_square(
    ecs_world: esper.World, player_cfg: dict, spawn_pos: dict
) -> int:
    size: pygame.Vector2 = pygame.Vector2(
        player_cfg["size"]["x"], player_cfg["size"]["y"]
    )
    player_entity = create_square(
        ecs_world,
        pos=pygame.Vector2(
            spawn_pos["position"]["x"] - size.x / 2,
            spawn_pos["position"]["y"] - size.y / 2,
        ),
        vel=pygame.Vector2(0, 0),
        size=size,
        color=pygame.Color(
            player_cfg["color"]["r"], player_cfg["color"]["g"], player_cfg["color"]["b"]
        ),
    )
    ecs_world.add_component(player_entity, CTagPlayer())
    return player_entity


def create_input_player(ecs_world: esper.World) -> None:
    input_left = ecs_world.create_entity()
    input_right = ecs_world.create_entity()
    input_up = ecs_world.create_entity()
    input_down = ecs_world.create_entity()

    ecs_world.add_component(
        input_left, CInputCommand(name="PLAYER_LEFT", key=pygame.K_LEFT)
    )
    ecs_world.add_component(
        input_right, CInputCommand(name="PLAYER_RIGHT", key=pygame.K_RIGHT)
    )
    ecs_world.add_component(input_up, CInputCommand(name="PLAYER_UP", key=pygame.K_UP))
    ecs_world.add_component(
        input_down, CInputCommand(name="PLAYER_DOWN", key=pygame.K_DOWN)
    )
