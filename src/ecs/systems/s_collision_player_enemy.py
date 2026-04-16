import esper

from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_enemy import CTagEnemy


def system_collision_player_enemy(
    world: esper.World, player_entity: int, level_cf: dict
) -> None:

    components = world.get_components(CSurface, CTransform, CTagEnemy)

    pl_t = world.component_for_entity(player_entity, CTransform)
    pl_s = world.component_for_entity(player_entity, CSurface)

    pl_rect = CSurface.get_area_relative(pl_s.area, pl_t.pos)

    for enemy_entity, (c_s, c_t, _) in components:
        enemy_rect = CSurface.get_area_relative(c_s.area, c_t.pos)

        if enemy_rect.colliderect(pl_rect):
            world.delete_entity(enemy_entity)
            pl_t.pos.x = (
                level_cf["player_spawn"]["position"]["x"] - pl_s.surf.get_width() / 2
            )
            pl_t.pos.y = (
                level_cf["player_spawn"]["position"]["y"] - pl_s.surf.get_height() / 2
            )
