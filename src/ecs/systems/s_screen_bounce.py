import esper
import pygame

from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.c_surface import CSurface
from src.ecs.components.tags.c_tag_enemy import CTagEnemy

def system_screen_bounce(world: esper.World, screen: pygame.Surface):
    screen_rect = screen.get_rect()
    components = world.get_components(CTransform, CVelocity, CSurface, CTagEnemy)

    c_transform: CTransform
    c_velocity: CVelocity
    c_surface: CSurface
    c_tag_enemy: CTagEnemy
    for _, (c_transform, c_velocity, c_surface, c_tag_enemy) in components:
        cuad_rect = c_surface.surf.get_rect(topleft=c_transform.pos)

        if (cuad_rect.left < screen_rect.left) or (cuad_rect.right > screen_rect.right):
            c_velocity.vel.x *= -1
            cuad_rect.clamp_ip(screen_rect)
            c_transform.pos.x = cuad_rect.x

        if (cuad_rect.top < screen_rect.top) or (cuad_rect.bottom > screen_rect.bottom):
            c_velocity.vel.y *= -1
            cuad_rect.clamp_ip(screen_rect)
            c_transform.pos.y = cuad_rect.y