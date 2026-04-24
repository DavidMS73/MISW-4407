import pygame


class CUiText:
    def __init__(
        self,
        text_id: str,
        font_path: str,
        size: int,
        color: pygame.Color,
        dynamic: bool = False,
    ) -> None:
        self.text_id = text_id
        self.font_path = font_path
        self.size = size
        self.color = color
        self.dynamic = dynamic
        self.current_text = ""
