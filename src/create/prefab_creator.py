import esper
import pygame

from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity

def crear_cuadrado(ecs_world: esper.World, pos: pygame.Vector2, vel: pygame.Vector2, size: pygame.Vector2, color: pygame.Color):
    cuad_entity = ecs_world.create_entity()
    ecs_world.add_component(cuad_entity, CSurface(size=size, color=color))
    ecs_world.add_component(cuad_entity, CTransform(pos=pos))
    ecs_world.add_component(cuad_entity, CVelocity(vel=vel))