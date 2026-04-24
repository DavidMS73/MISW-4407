class CPlayerSpecialDefense:
    def __init__(self, duration: float, cooldown: float, radius: float, sound: str) -> None:
        self.duration = duration
        self.cooldown = cooldown
        self.radius = radius
        self.sound = sound
        self.shield_entity: int | None = None
        self.active_time_left = 0.0
        self.cooldown_time_left = 0.0

    def try_activate(self) -> bool:
        if self.active_time_left > 0 or self.cooldown_time_left > 0:
            return False
        self.active_time_left = self.duration
        self.cooldown_time_left = self.cooldown
        return True

    def update_timers(self, delta_time: float) -> None:
        if self.active_time_left > 0:
            self.active_time_left = max(0.0, self.active_time_left - delta_time)
        if self.cooldown_time_left > 0:
            self.cooldown_time_left = max(0.0, self.cooldown_time_left - delta_time)

    @property
    def is_active(self) -> bool:
        return self.active_time_left > 0

    @property
    def is_on_cooldown(self) -> bool:
        return self.cooldown_time_left > 0
