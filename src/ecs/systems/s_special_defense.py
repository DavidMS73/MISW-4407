import esper
import pygame

from src.create.prefab_creator import create_explosion
from src.ecs.components.c_player_special_defense import CPlayerSpecialDefense
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_enemy import CTagEnemy


def system_special_defense(
    world: esper.World,
    player_entity: int,
    delta_time: float,
    explosion_cfg: dict,
) -> int:
    special_defense = world.component_for_entity(player_entity, CPlayerSpecialDefense)
    special_defense.update_timers(delta_time)

    if special_defense.shield_entity is not None and not world.entity_exists(
        special_defense.shield_entity
    ):
        special_defense.shield_entity = None

    if not special_defense.is_active:
        if special_defense.shield_entity is not None:
            world.delete_entity(special_defense.shield_entity)
            special_defense.shield_entity = None
        return 0

    player_transform = world.component_for_entity(player_entity, CTransform)
    player_surface = world.component_for_entity(player_entity, CSurface)
    player_center = pygame.Vector2(
        player_transform.pos.x + player_surface.area.w / 2,
        player_transform.pos.y + player_surface.area.h / 2,
    )

    if special_defense.shield_entity is not None:
        shield_transform = world.component_for_entity(
            special_defense.shield_entity, CTransform
        )
        shield_surface = world.component_for_entity(special_defense.shield_entity, CSurface)
        shield_transform.pos.x = player_center.x - shield_surface.area.w / 2
        shield_transform.pos.y = player_center.y - shield_surface.area.h / 2

    enemies = world.get_components(CTransform, CSurface, CTagEnemy)
    enemies_to_delete: set[int] = set()

    for enemy_entity, (enemy_transform, enemy_surface, _) in enemies:
        enemy_center = pygame.Vector2(
            enemy_transform.pos.x + enemy_surface.area.w / 2,
            enemy_transform.pos.y + enemy_surface.area.h / 2,
        )
        if player_center.distance_to(enemy_center) <= special_defense.radius:
            create_explosion(world, enemy_center, explosion_cfg)
            enemies_to_delete.add(enemy_entity)

    for enemy_entity in enemies_to_delete:
        world.delete_entity(enemy_entity)

    return len(enemies_to_delete)
