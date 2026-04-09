import esper
import pygame

from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_surface import CSurface

def system_rendering(world: esper.World, screen: pygame.Surface):
    components = world.get_components(CTransform, CSurface)

    c_transform: CTransform
    c_surface: CSurface
    for entity, (c_transform, c_surface) in components:
        screen.blit(c_surface.surf, c_transform.pos)