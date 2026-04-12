import json
from pathlib import Path

import pygame
import esper

from src.create.prefab_creator import (
    create_enemy_spawner,
    create_input_player,
    create_player_square,
)
from src.ecs.systems.s_collision_player_enemy import system_collision_player_enemy
from src.ecs.systems.s_movement import system_movement
from src.ecs.systems.s_enemy_spawner import system_enemy_spawner
from src.ecs.systems.s_rendering import system_rendering
from src.ecs.systems.s_screen_bounce import system_screen_bounce
from src.ecs.systems.s_input_player import system_input_player

from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.c_input_command import CInputCommand, CommandPhase


class GameEngine:
    def __init__(self) -> None:
        self.cfg_dir = Path("assets/cfg")
        self.window_cfg = self._load_json_config("window.json")
        self.enemy_types_cfg = self._load_json_config("enemies.json")
        self.level_cfg = self._load_json_config("level_01.json")
        self.player_cfg = self._load_json_config("player.json")

        window_size = self.window_cfg["size"]
        bg_color = self.window_cfg["bg_color"]

        pygame.init()
        pygame.display.set_caption(self.window_cfg["title"])
        self.screen = pygame.display.set_mode(
            (window_size["w"], window_size["h"]), pygame.SCALED
        )
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
        self._player_entity = create_player_square(
            self.ecs_world, self.player_cfg, self.level_cfg["player_spawn"]
        )
        self._player_c_v = self.ecs_world.component_for_entity(
            self._player_entity, CVelocity
        )

        create_enemy_spawner(self.ecs_world, self.enemy_types_cfg, self.level_cfg)
        create_input_player(self.ecs_world)

    def _calculate_time(self):
        self.clock.tick(self.framerate)
        self.delta_time = self.clock.get_time() / 1000.0

    def _process_events(self):
        for event in pygame.event.get():
            system_input_player(self.ecs_world, event, self._do_action)
            if event.type == pygame.QUIT:
                self.is_running = False

    def _update(self):
        system_enemy_spawner(self.ecs_world, self.delta_time)
        system_movement(self.ecs_world, self.delta_time)
        system_screen_bounce(self.ecs_world, self.screen)
        system_collision_player_enemy(
            self.ecs_world, self._player_entity, self.level_cfg
        )
        self.ecs_world._clear_dead_entities()

    def _draw(self):
        self.screen.fill(self.bg_color)
        system_rendering(self.ecs_world, self.screen)
        pygame.display.flip()

    def _clean(self):
        self.ecs_world.clear_database()
        pygame.quit()

    def _do_action(self, c_input: CInputCommand):
        if c_input.name == "PLAYER_LEFT":
            if c_input.phase == CommandPhase.START:
                self._player_c_v.vel.x -= self.player_cfg["input_velocity"]
            elif c_input.phase == CommandPhase.END:
                self._player_c_v.vel.x += self.player_cfg["input_velocity"]
        elif c_input.name == "PLAYER_RIGHT":
            if c_input.phase == CommandPhase.START:
                self._player_c_v.vel.x += self.player_cfg["input_velocity"]
            elif c_input.phase == CommandPhase.END:
                self._player_c_v.vel.x -= self.player_cfg["input_velocity"]
        elif c_input.name == "PLAYER_UP":
            if c_input.phase == CommandPhase.START:
                self._player_c_v.vel.y -= self.player_cfg["input_velocity"]
            elif c_input.phase == CommandPhase.END:
                self._player_c_v.vel.y += self.player_cfg["input_velocity"]
        elif c_input.name == "PLAYER_DOWN":
            if c_input.phase == CommandPhase.START:
                self._player_c_v.vel.y += self.player_cfg["input_velocity"]
            elif c_input.phase == CommandPhase.END:
                self._player_c_v.vel.y -= self.player_cfg["input_velocity"]
