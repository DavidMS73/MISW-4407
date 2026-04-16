import esper
import pygame

from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_bullet import CTagBullet


def system_screen_bullet(world: esper.World, screen: pygame.Surface) -> None:
    screen_rect = screen.get_rect()
    components = world.get_components(CTransform, CSurface, CTagBullet)

    for entity, (c_transform, c_surface, _) in components:
        bullet_rect = CSurface.get_area_relative(c_surface.area, c_transform.pos)
        if not screen_rect.contains(bullet_rect):
            world.delete_entity(entity)
