import json
from pathlib import Path

import pygame
import esper

from src.ecs.components.c_enemy_spawner import CEnemySpawner, EnemyTypeData, SpawnEvent
from src.ecs.systems.s_movement import system_movement
from src.ecs.systems.s_enemy_spawner import system_enemy_spawner
from src.ecs.systems.s_rendering import system_rendering
from src.ecs.systems.s_screen_bounce import system_screen_bounce


class GameEngine:
    def __init__(self) -> None:
        self.cfg_dir = Path("assets/cfg")
        self.window_cfg = self._load_json_config("window.json")
        self.enemy_types_cfg = self._load_json_config("enemies.json")
        self.level_cfg = self._load_json_config("level_01.json")

        window_size = self.window_cfg["size"]
        bg_color = self.window_cfg["bg_color"]

        pygame.init()
        pygame.display.set_caption(self.window_cfg["title"])
        self.screen = pygame.display.set_mode((window_size["w"], window_size["h"]), pygame.SCALED)
        self.clock = pygame.time.Clock()
        self.is_running = False
        self.framerate = self.window_cfg["framerate"]
        self.bg_color = pygame.Color(bg_color["r"], bg_color["g"], bg_color["b"])
        self.delta_time = 0

        self.ecs_world = esper.World()

    def _load_json_config(self, file_name: str) -> dict:
        file_path = self.cfg_dir / file_name
        with file_path.open("r", encoding="utf-8") as cfg_file:
            return json.load(cfg_file)

    def _build_enemy_types(self) -> dict[str, EnemyTypeData]:
        enemy_types: dict[str, EnemyTypeData] = {}
        for enemy_type, enemy_data in self.enemy_types_cfg.items():
            enemy_types[enemy_type] = EnemyTypeData(
                size=pygame.Vector2(enemy_data["size"]["x"], enemy_data["size"]["y"]),
                color=pygame.Color(
                    enemy_data["color"]["r"],
                    enemy_data["color"]["g"],
                    enemy_data["color"]["b"],
                ),
                velocity_min=enemy_data["velocity_min"],
                velocity_max=enemy_data["velocity_max"],
            )
        return enemy_types

    def _build_spawn_events(self) -> list[SpawnEvent]:
        events: list[SpawnEvent] = []
        for event in self.level_cfg["enemy_spawn_events"]:
            events.append(
                SpawnEvent(
                    time=event["time"],
                    enemy_type=event["enemy_type"],
                    position=pygame.Vector2(event["position"]["x"], event["position"]["y"]),
                )
            )
        events.sort(key=lambda spawn_event: spawn_event.time)
        return events

    def run(self) -> None:
        self._create()
        self.is_running = True
        while self.is_running:
            self._calculate_time()
            self._process_events()
            self._update()
            self._draw()
        self._clean()

    def _create(self):
        spawner_entity = self.ecs_world.create_entity()
        c_enemy_spawner = CEnemySpawner(
            spawn_events=self._build_spawn_events(),
            enemy_types=self._build_enemy_types(),
        )
        self.ecs_world.add_component(spawner_entity, c_enemy_spawner)

    def _calculate_time(self):
        self.clock.tick(self.framerate)
        self.delta_time = self.clock.get_time() / 1000.0

    def _process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False

    def _update(self):
        system_enemy_spawner(self.ecs_world, self.delta_time)
        system_movement(self.ecs_world, self.delta_time)
        system_screen_bounce(self.ecs_world, self.screen)

    def _draw(self):
        self.screen.fill(self.bg_color)

        system_rendering(self.ecs_world, self.screen)
        pygame.display.flip()

    def _clean(self):
        pygame.quit()
