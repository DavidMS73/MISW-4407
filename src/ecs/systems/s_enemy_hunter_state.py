import esper
import pygame

from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_hunter_state import CHunterState, HunterMode
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity


RETURN_ARRIVAL_EPSILON = 2.0


def system_enemy_hunter_state(
    world: esper.World, player_entity: int
) -> None:
    player_transform = world.component_for_entity(player_entity, CTransform)
    player_surface = world.component_for_entity(player_entity, CSurface)
    player_center = pygame.Vector2(
        player_transform.pos.x + player_surface.area.w / 2,
        player_transform.pos.y + player_surface.area.h / 2,
    )

    components = world.get_components(
        CHunterState, CTransform, CVelocity, CAnimation, CSurface
    )

    for _, (c_hunter_state, c_transform, c_velocity, c_animation, c_surface) in components:
        enemy_center = pygame.Vector2(
            c_transform.pos.x + c_surface.area.w / 2,
            c_transform.pos.y + c_surface.area.h / 2,
        )

        distance_to_player = player_center.distance_to(enemy_center)
        distance_to_spawn = c_hunter_state.spawn_pos.distance_to(enemy_center)

        if c_hunter_state.mode == HunterMode.RETURN:
            _do_enemy_hunter_return(
                c_hunter_state,
                c_transform,
                c_velocity,
                c_animation,
                c_surface,
                distance_to_spawn,
            )
        elif c_hunter_state.mode == HunterMode.CHASE:
            _do_enemy_hunter_chase(
                c_hunter_state,
                c_transform,
                c_velocity,
                c_animation,
                c_surface,
                player_center,
                distance_to_player,
                distance_to_spawn,
            )
        else:
            _do_enemy_hunter_idle(
                c_hunter_state,
                c_transform,
                c_velocity,
                c_animation,
                c_surface,
                distance_to_player,
                distance_to_spawn,
            )


def _do_enemy_hunter_idle(
    c_hunter_state: CHunterState,
    c_transform: CTransform,
    c_velocity: CVelocity,
    c_animation: CAnimation,
    c_surface: CSurface,
    distance_to_player: float,
    distance_to_spawn: float,
) -> None:
    c_velocity.vel = pygame.Vector2(0, 0)
    c_animation.set_animation("IDLE")

    if distance_to_spawn >= c_hunter_state.distance_start_return:
        c_hunter_state.mode = HunterMode.RETURN
    elif distance_to_player <= c_hunter_state.distance_start_chase:
        c_hunter_state.mode = HunterMode.CHASE


def _do_enemy_hunter_chase(
    c_hunter_state: CHunterState,
    c_transform: CTransform,
    c_velocity: CVelocity,
    c_animation: CAnimation,
    c_surface: CSurface,
    player_center: pygame.Vector2,
    distance_to_player: float,
    distance_to_spawn: float,
) -> None:
    if distance_to_spawn >= c_hunter_state.distance_start_return:
        c_hunter_state.mode = HunterMode.RETURN
        return

    enemy_center = pygame.Vector2(
        c_transform.pos.x + c_surface.area.w / 2,
        c_transform.pos.y + c_surface.area.h / 2,
    )

    if distance_to_player <= c_hunter_state.distance_start_chase:
        direction = player_center - enemy_center
        if direction.length_squared() > 0:
            c_velocity.vel = direction.normalize() * c_hunter_state.velocity_chase
        c_animation.set_animation("MOVE")
    else:
        c_velocity.vel = pygame.Vector2(0, 0)
        c_animation.set_animation("IDLE")
        c_hunter_state.mode = HunterMode.RETURN


def _do_enemy_hunter_return(
    c_hunter_state: CHunterState,
    c_transform: CTransform,
    c_velocity: CVelocity,
    c_animation: CAnimation,
    c_surface: CSurface,
    distance_to_spawn: float,
) -> None:
    enemy_center = pygame.Vector2(
        c_transform.pos.x + c_surface.area.w / 2,
        c_transform.pos.y + c_surface.area.h / 2,
    )
    direction = c_hunter_state.spawn_pos - enemy_center

    if distance_to_spawn > RETURN_ARRIVAL_EPSILON and direction.length_squared() > 0:
        c_velocity.vel = direction.normalize() * c_hunter_state.velocity_return
        c_animation.set_animation("MOVE")
    else:
        c_velocity.vel = pygame.Vector2(0, 0)
        c_animation.set_animation("IDLE")
        c_hunter_state.mode = HunterMode.IDLE
