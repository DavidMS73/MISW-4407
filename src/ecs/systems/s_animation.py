import esper

from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_surface import CSurface


def system_animation(world: esper.World, dt: float) -> None:
    components = world.get_components(CSurface, CAnimation)

    for _, (c_surface, c_animation) in components:
        c_animation.curr_anim_time -= dt

        if c_animation.curr_anim_time <= 0:

            c_animation.curr_anim_time = c_animation.animations_list[
                c_animation.curr_anim
            ].framerate

            c_animation.curr_frame += 1

            if (
                c_animation.curr_frame
                > c_animation.animations_list[c_animation.curr_anim].end
            ):
                c_animation.curr_frame = c_animation.animations_list[
                    c_animation.curr_anim
                ].start

            rect_surf = c_surface.surf.get_rect()
            c_surface.area.w = rect_surf.w / c_animation.number_frames
            c_surface.area.x = c_surface.area.w * c_animation.curr_frame
