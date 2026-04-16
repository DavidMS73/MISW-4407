import esper
import pygame

from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_player import CTagPlayer


def system_screen_player(world: esper.World, screen: pygame.Surface) -> None:
    screen_w = screen.get_width()
    screen_h = screen.get_height()
    components = world.get_components(CTransform, CSurface, CTagPlayer)

    for _, (c_transform, c_surface, _) in components:
        max_x = screen_w - c_surface.area.width
        max_y = screen_h - c_surface.area.height

        if c_transform.pos.x < 0:
            c_transform.pos.x = 0
        elif c_transform.pos.x > max_x:
            c_transform.pos.x = max_x

        if c_transform.pos.y < 0:
            c_transform.pos.y = 0
        elif c_transform.pos.y > max_y:
            c_transform.pos.y = max_y
