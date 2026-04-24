import esper
import pygame

from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_ui_text import CUiText
from src.engine.service_locator import ServiceLocator


def _build_text(c_ui_text: CUiText, state: dict, static_texts: dict[str, str]) -> str:
    if not c_ui_text.dynamic:
        return static_texts.get(c_ui_text.text_id, "")

    if c_ui_text.text_id == "PAUSE_STATUS":
        return "JUEGO PAUSADO (P para continuar)" if state["paused"] else ""

    if c_ui_text.text_id == "SPECIAL_STATUS":
        if state["special_active"] > 0:
            return f"DEFENSA ACTIVA: {state['special_active']:.1f}s"
        if state["special_cooldown"] > 0:
            return f"Recarga defensa: {state['special_cooldown']:.1f}s"
        return "Defensa lista (ESPACIO)"

    if c_ui_text.text_id == "BULLET_STATUS":
        return f"Balas: {state['bullets']}"

    return ""


def system_ui_text(world: esper.World, state: dict, static_texts: dict[str, str]) -> None:
    components = world.get_components(CUiText, CSurface)

    for _, (c_ui_text, c_surface) in components:
        text = _build_text(c_ui_text, state, static_texts)
        if text == c_ui_text.current_text:
            continue

        font = ServiceLocator.fonts_service.get(c_ui_text.font_path, c_ui_text.size)
        c_ui_text.current_text = text

        if not text:
            c_surface.surf = pygame.Surface((1, 1), pygame.SRCALPHA)
            c_surface.area = c_surface.surf.get_rect()
            continue

        new_surface = CSurface.from_text(text, font, c_ui_text.color)
        c_surface.surf = new_surface.surf
        c_surface.area = new_surface.area
