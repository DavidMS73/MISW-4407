import esper

from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_bullet import CTagBullet
from src.ecs.components.tags.c_tag_enemy import CTagEnemy


def system_collision_enemy_bullet(world: esper.World) -> None:
    bullets = world.get_components(CSurface, CTransform, CTagBullet)
    enemies = world.get_components(CSurface, CTransform, CTagEnemy)

    bullet_items = list(bullets)
    enemy_items = list(enemies)

    bullets_to_delete: set[int] = set()
    enemies_to_delete: set[int] = set()

    for bullet_entity, (bullet_surface, bullet_transform, _) in bullet_items:
        bullet_rect = CSurface.get_area_relative(bullet_surface.area, bullet_transform.pos)

        for enemy_entity, (enemy_surface, enemy_transform, _) in enemy_items:
            enemy_rect = CSurface.get_area_relative(enemy_surface.area, enemy_transform.pos)

            if bullet_rect.colliderect(enemy_rect):
                bullets_to_delete.add(bullet_entity)
                enemies_to_delete.add(enemy_entity)
                break

    for entity in bullets_to_delete:
        world.delete_entity(entity)

    for entity in enemies_to_delete:
        world.delete_entity(entity)
