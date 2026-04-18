import esper

from src.ecs.components.c_animation import CAnimation
from src.ecs.components.tags.c_tag_explosion import CTagExplosion


def system_explosion_lifecycle(world: esper.World) -> None:
    components = world.get_components(CAnimation, CTagExplosion)

    for entity, (c_animation, _) in components:
        if c_animation.is_over:
            world.delete_entity(entity)
