import esper

from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_surface import CSurface


def system_animation(world: esper.World, dt: float) -> None:
    components = world.get_components(CSurface, CAnimation)

    for _, (c_surface, c_animation) in components:
        if c_animation.is_over:
            continue

        c_animation.curr_anim_time -= dt

        if c_animation.curr_anim_time <= 0:
            curr_animation = c_animation.animations_list[c_animation.curr_anim]

            c_animation.curr_anim_time = curr_animation.framerate

            c_animation.curr_frame += 1

            if c_animation.curr_frame > curr_animation.end:
                if curr_animation.loop:
                    c_animation.curr_frame = curr_animation.start
                else:
                    c_animation.curr_frame = curr_animation.end
                    c_animation.is_over = True

            rect_surf = c_surface.surf.get_rect()
            c_surface.area.w = int(rect_surf.w / c_animation.number_frames)
            c_surface.area.x = c_surface.area.w * c_animation.curr_frame
