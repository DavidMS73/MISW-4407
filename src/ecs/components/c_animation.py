class CAnimation:
    def __init__(self, animations: dict) -> None:
        self.number_frames = animations["number_frames"]
        self.animations_by_name = {}
        self.animations_list = []
        for anim in animations["list"]:
            anim_data = AnimationData(
                anim["name"],
                anim["start"],
                anim["end"],
                anim["framerate"],
                anim.get("loop", anim["name"] != "EXPLODE"),
            )
            self.animations_by_name[anim_data.name] = len(self.animations_list)
            self.animations_list.append(anim_data)

        self.curr_anim = 0
        self.curr_anim_time = 0
        self.curr_frame = self.animations_list[self.curr_anim].start
        self.is_over = False

    def set_animation(self, animation_name: str) -> None:
        next_anim = self.animations_by_name.get(animation_name)
        if next_anim is None or next_anim == self.curr_anim:
            return

        self.curr_anim = next_anim
        self.curr_anim_time = 0
        self.curr_frame = self.animations_list[self.curr_anim].start
        self.is_over = False


class AnimationData:
    def __init__(
        self, name: str, start: int, end: int, framerate: float, loop: bool
    ) -> None:
        self.name = name
        self.start = start
        self.end = end
        self.framerate = 1.0 / framerate
        self.loop = loop
