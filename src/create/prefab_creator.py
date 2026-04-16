import math
import random

import esper
import pygame

from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_enemy_spawner import CEnemySpawner, EnemyTypeData, SpawnEvent
from src.ecs.components.c_player_state import CPlayerState
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.c_input_command import CInputCommand
from src.ecs.components.tags.c_tag_bullet import CTagBullet
from src.ecs.components.tags.c_tag_enemy import CTagEnemy
from src.ecs.components.tags.c_tag_player import CTagPlayer


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


def create_sprite(
    ecs_world: esper.World,
    pos: pygame.Vector2,
    vel: pygame.Vector2,
    surface: pygame.Surface,
) -> int:
    sprite_entity = ecs_world.create_entity()
    ecs_world.add_component(sprite_entity, CTransform(pos=pos))
    ecs_world.add_component(sprite_entity, CVelocity(vel=vel))
    ecs_world.add_component(sprite_entity, CSurface.from_surface(surface))
    return sprite_entity


def _build_enemy_types(enemy_types_cfg: dict) -> dict[str, EnemyTypeData]:
    enemy_types: dict[str, EnemyTypeData] = {}
    for enemy_type, enemy_data in enemy_types_cfg.items():
        enemy_types[enemy_type] = EnemyTypeData(
            image=pygame.image.load(enemy_data["image"]).convert_alpha(),
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


def _build_spawn_velocity(enemy_type_data: EnemyTypeData) -> pygame.Vector2:
    speed = random.uniform(enemy_type_data.velocity_min, enemy_type_data.velocity_max)
    angle = random.uniform(0.0, math.tau)
    return pygame.Vector2(math.cos(angle), math.sin(angle)) * speed


def _spawn_enemy(
    world: esper.World, event: SpawnEvent, enemy_type_data: EnemyTypeData
) -> None:
    enemy_entity = create_sprite(
        world,
        pos=pygame.Vector2(event.position.x, event.position.y),
        vel=_build_spawn_velocity(enemy_type_data),
        surface=enemy_type_data.image,
    )
    world.add_component(enemy_entity, CTagEnemy())


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
    player_sprite = pygame.image.load(player_cfg["image"]).convert_alpha()
    size = player_sprite.get_size()
    size = (size[0] / player_cfg["animations"]["number_frames"], size[1])
    player_entity = create_sprite(
        ecs_world,
        pos=pygame.Vector2(
            spawn_pos["position"]["x"] - size[0] / 2,
            spawn_pos["position"]["y"] - size[1] / 2,
        ),
        vel=pygame.Vector2(0, 0),
        surface=player_sprite,
    )
    ecs_world.add_component(player_entity, CTagPlayer())
    ecs_world.add_component(player_entity, CAnimation(player_cfg["animations"]))
    ecs_world.add_component(player_entity, CPlayerState())
    return player_entity


def create_bullet_square(
    ecs_world: esper.World,
    pos: pygame.Vector2,
    vel: pygame.Vector2,
    surface: pygame.Surface,
) -> int:
    bullet_entity = create_sprite(ecs_world, pos=pos, vel=vel, surface=surface)
    ecs_world.add_component(bullet_entity, CTagBullet())
    return bullet_entity


def spawn_player_bullet(
    ecs_world: esper.World,
    player_transform: CTransform,
    player_surface: CSurface,
    bullet_cfg: dict,
) -> int:
    mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
    player_center = pygame.Vector2(
        player_transform.pos.x + player_surface.area.w / 2,
        player_transform.pos.y + player_surface.area.h / 2,
    )
    direction = mouse_pos - player_center
    if direction.length_squared() == 0:
        direction = pygame.Vector2(0, -1)
    else:
        direction = direction.normalize()

    bullet_surface = pygame.image.load(bullet_cfg["image"]).convert_alpha()
    bullet_velocity = direction * bullet_cfg["velocity"]
    bullet_pos = (
        player_center
        - pygame.Vector2(bullet_surface.get_width(), bullet_surface.get_height()) / 2
    )

    return create_bullet_square(
        ecs_world,
        pos=bullet_pos,
        vel=bullet_velocity,
        surface=bullet_surface,
    )


def create_input_player(ecs_world: esper.World) -> None:
    input_left = ecs_world.create_entity()
    input_right = ecs_world.create_entity()
    input_up = ecs_world.create_entity()
    input_down = ecs_world.create_entity()
    input_fire = ecs_world.create_entity()

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
    ecs_world.add_component(
        input_fire, CInputCommand(name="PLAYER_FIRE", key=pygame.BUTTON_LEFT)
    )
