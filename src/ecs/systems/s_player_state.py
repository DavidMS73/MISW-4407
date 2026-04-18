import esper

from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_player_state import CPlayerState, PlayerState
from src.ecs.components.c_velocity import CVelocity


def system_player_state(world: esper.World) -> None:
    components = world.get_components(CVelocity, CAnimation, CPlayerState)

    for _, (c_velocity, c_animation, c_player_state) in components:
        if c_player_state.state == PlayerState.IDLE:
            _do_idle_state(c_velocity, c_animation, c_player_state)
        elif c_player_state.state == PlayerState.MOVE:
            _do_move_state(c_velocity, c_animation, c_player_state)


def _do_idle_state(
    c_velocity: CVelocity, c_animation: CAnimation, c_player_state: CPlayerState
) -> None:
    c_animation.set_animation("IDLE")
    if c_velocity.vel.magnitude_squared() > 0:
        c_player_state.state = PlayerState.MOVE


def _do_move_state(
    c_velocity: CVelocity, c_animation: CAnimation, c_player_state: CPlayerState
) -> None:
    c_animation.set_animation("MOVE")
    if c_velocity.vel.magnitude_squared() <= 0:
        c_player_state.state = PlayerState.IDLE
