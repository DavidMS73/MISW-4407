import pygame


class CSurface:
    def __init__(self, size=pygame.Vector2, color=pygame.Color):
        self.surf = pygame.Surface(size)
        self.surf.fill(color)
        self.area = self.surf.get_rect()

    @classmethod
    def from_surface(cls, surface: pygame.Surface) -> "CSurface":
        c_surface = cls(pygame.Vector2(0, 0), pygame.Color(0, 0, 0))
        c_surface.surf = surface
        c_surface.area = surface.get_rect()

        return c_surface

    def get_area_relative(
        area: pygame.Rect, pos_topleft: pygame.Vector2
    ) -> pygame.Rect:
        new_rect = area.copy()
        new_rect.topleft = pos_topleft.copy()
        return new_rect
