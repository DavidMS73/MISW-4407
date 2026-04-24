import math
import random

import esper
import pygame

from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_enemy_spawner import CEnemySpawner, EnemyTypeData, SpawnEvent
from src.ecs.components.c_hunter_state import CHunterState, HunterMode
from src.ecs.components.c_player_state import CPlayerState
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.c_input_command import CInputCommand
from src.ecs.components.tags.c_tag_bullet import CTagBullet
from src.ecs.components.tags.c_tag_enemy import CTagEnemy
from src.ecs.components.tags.c_tag_explosion import CTagExplosion
from src.ecs.components.tags.c_tag_player import CTagPlayer
from src.engine.service_locator import ServiceLocator


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


def _setup_animation_area(c_surface: CSurface, c_animation: CAnimation) -> None:
    curr_animation = c_animation.animations_list[c_animation.curr_anim]
    frame_width = int(c_surface.surf.get_width() / c_animation.number_frames)
    c_surface.area.w = frame_width
    c_surface.area.h = c_surface.surf.get_height()
    c_surface.area.x = frame_width * curr_animation.start
    c_surface.area.y = 0


def _build_enemy_types(enemy_types_cfg: dict) -> dict[str, EnemyTypeData]:
    enemy_types: dict[str, EnemyTypeData] = {}
    for enemy_type, enemy_data in enemy_types_cfg.items():
        enemy_types[enemy_type] = EnemyTypeData(
            image=ServiceLocator.images_service.get(enemy_data["image"]),
            sound=enemy_data.get("sound"),
            sound_chase=enemy_data.get("sound_chase"),
            velocity_min=enemy_data.get("velocity_min", 0),
            velocity_max=enemy_data.get("velocity_max", 0),
            animations=enemy_data.get("animations"),
            velocity_chase=enemy_data.get("velocity_chase"),
            velocity_return=enemy_data.get("velocity_return"),
            distance_start_chase=enemy_data.get("distance_start_chase"),
            distance_start_return=enemy_data.get("distance_start_return"),
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
    number_frames = 1
    if enemy_type_data.animations is not None:
        number_frames = enemy_type_data.animations["number_frames"]

    frame_width = enemy_type_data.image.get_width() / number_frames
    frame_height = enemy_type_data.image.get_height()

    enemy_entity = create_sprite(
        world,
        pos=pygame.Vector2(event.position.x, event.position.y),
        vel=_build_spawn_velocity(enemy_type_data),
        surface=enemy_type_data.image,
    )
    world.add_component(enemy_entity, CTagEnemy(event.enemy_type))

    if enemy_type_data.animations is not None:
        world.add_component(enemy_entity, CAnimation(enemy_type_data.animations))
        c_surface = world.component_for_entity(enemy_entity, CSurface)
        c_animation = world.component_for_entity(enemy_entity, CAnimation)
        _setup_animation_area(c_surface, c_animation)

    if event.enemy_type == "Hunter":
        world.add_component(
            enemy_entity,
            CHunterState(
                spawn_pos=pygame.Vector2(
                    event.position.x + frame_width / 2,
                    event.position.y + frame_height / 2,
                ),
                sound_chase=enemy_type_data.sound_chase,
                velocity_chase=enemy_type_data.velocity_chase,
                velocity_return=enemy_type_data.velocity_return,
                distance_start_chase=enemy_type_data.distance_start_chase,
                distance_start_return=enemy_type_data.distance_start_return,
                mode=HunterMode.IDLE,
            ),
        )
    else:
        ServiceLocator.sounds_service.play(enemy_type_data.sound)


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
    player_sprite = ServiceLocator.images_service.get(player_cfg["image"])
    frame_width = player_sprite.get_width() / player_cfg["animations"]["number_frames"]
    frame_height = player_sprite.get_height()
    player_entity = create_sprite(
        ecs_world,
        pos=pygame.Vector2(
            spawn_pos["position"]["x"] - frame_width / 2,
            spawn_pos["position"]["y"] - frame_height / 2,
        ),
        vel=pygame.Vector2(0, 0),
        surface=player_sprite,
    )
    ecs_world.add_component(player_entity, CTagPlayer())
    ecs_world.add_component(player_entity, CAnimation(player_cfg["animations"]))
    _setup_animation_area(
        ecs_world.component_for_entity(player_entity, CSurface),
        ecs_world.component_for_entity(player_entity, CAnimation),
    )
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

    bullet_surface = ServiceLocator.images_service.get(bullet_cfg["image"])
    bullet_velocity = direction * bullet_cfg["velocity"]
    bullet_area = bullet_surface.get_rect()
    bullet_pos = player_center - pygame.Vector2(bullet_area.w, bullet_area.h) / 2

    entity = create_bullet_square(
        ecs_world,
        pos=bullet_pos,
        vel=bullet_velocity,
        surface=bullet_surface,
    )
    ServiceLocator.sounds_service.play(bullet_cfg["sound"])
    return entity


def create_explosion(
    ecs_world: esper.World, pos: pygame.Vector2, explosion_cfg: dict
) -> int:
    explosion_surface = ServiceLocator.images_service.get(explosion_cfg["image"])
    number_frames = explosion_cfg["animations"]["number_frames"]
    frame_width = explosion_surface.get_width() / number_frames
    frame_height = explosion_surface.get_height()

    explosion_entity = create_sprite(
        ecs_world,
        pos=pygame.Vector2(pos.x - frame_width / 2, pos.y - frame_height / 2),
        vel=pygame.Vector2(0, 0),
        surface=explosion_surface,
    )
    ecs_world.add_component(explosion_entity, CAnimation(explosion_cfg["animations"]))
    _setup_animation_area(
        ecs_world.component_for_entity(explosion_entity, CSurface),
        ecs_world.component_for_entity(explosion_entity, CAnimation),
    )
    ecs_world.add_component(explosion_entity, CTagExplosion())
    ServiceLocator.sounds_service.play(explosion_cfg["sound"])
    return explosion_entity


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
