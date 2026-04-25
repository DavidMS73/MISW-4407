import asyncio
import json
from pathlib import Path

import pygame
import esper

from src.create.prefab_creator import (
    create_interface_texts,
    create_enemy_spawner,
    create_input_player,
    create_player_square,
    create_special_defense_shield,
    spawn_player_bullet,
)
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.systems.s_animation import system_animation
from src.ecs.systems.s_collision_player_enemy import system_collision_player_enemy
from src.ecs.systems.s_collision_enemy_bullet import system_collision_enemy_bullet
from src.ecs.systems.s_enemy_hunter_state import system_enemy_hunter_state
from src.ecs.systems.s_explosion_lifecycle import system_explosion_lifecycle
from src.ecs.systems.s_movement import system_movement
from src.ecs.systems.s_enemy_spawner import system_enemy_spawner
from src.ecs.systems.s_player_state import system_player_state
from src.ecs.systems.s_rendering import system_rendering
from src.ecs.systems.s_special_defense import system_special_defense
from src.ecs.systems.s_screen_bounce import system_screen_bounce
from src.ecs.systems.s_screen_player import system_screen_player
from src.ecs.systems.s_screen_bullet import system_screen_bullet
from src.ecs.systems.s_ui_text import system_ui_text
from src.ecs.systems.s_input_player import system_input_player

from src.ecs.components.c_player_special_defense import CPlayerSpecialDefense
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.c_input_command import CInputCommand, CommandPhase
from src.ecs.components.tags.c_tag_bullet import CTagBullet
from src.engine.service_locator import ServiceLocator


class GameEngine:
    def __init__(self) -> None:
        self.cfg_dir = Path("assets/cfg")
        self.window_cfg = self._load_json_config("window.json")
        self.enemy_types_cfg = self._load_json_config("enemies.json")
        self.level_cfg = self._load_json_config("level_01.json")
        self.player_cfg = self._load_json_config("player.json")
        self.bullet_cfg = self._load_json_config("bullet.json")
        self.explosion_cfg = self._load_json_config("explosion.json")
        self.shield_cfg = self._load_json_config("shield.json")
        self.interface_cfg = self._load_json_config("interface.json")

        window_size = self.window_cfg["size"]
        bg_color = self.window_cfg["bg_color"]

        pygame.init()
        pygame.display.set_caption(self.window_cfg["title"])
        self.screen = pygame.display.set_mode(
            (window_size["w"], window_size["h"]), 0
        )
        self.clock = pygame.time.Clock()
        self.is_running = False
        self.framerate = self.window_cfg["framerate"]
        self.bg_color = pygame.Color(bg_color["r"], bg_color["g"], bg_color["b"])
        self.delta_time = 0
        self.elapsed_time = 0
        self._player_bullet_count = 0
        self._is_paused = False
        self._is_player_moving = False
        self._ui_static_texts: dict[str, str] = {}

        self.ecs_world = esper.World()

    def _load_json_config(self, file_name: str) -> dict:
        file_path = self.cfg_dir / file_name
        with file_path.open("r", encoding="utf-8") as cfg_file:
            return json.load(cfg_file)

    async def run(self) -> None:
        self._create()
        self.is_running = True
        while self.is_running:
            self._calculate_time()
            self._process_events()
            self._update()
            self._draw()
            await asyncio.sleep(0)  # Yield control to the event loop
        self._clean()

    def _create(self):
        self._player_entity = create_player_square(
            self.ecs_world,
            self.player_cfg,
            self.level_cfg["player_spawn"],
            self.shield_cfg,
        )
        self._player_c_v = self.ecs_world.component_for_entity(
            self._player_entity, CVelocity
        )
        self._player_c_t = self.ecs_world.component_for_entity(
            self._player_entity, CTransform
        )
        self._player_c_s = self.ecs_world.component_for_entity(
            self._player_entity, CSurface
        )

        create_enemy_spawner(self.ecs_world, self.enemy_types_cfg, self.level_cfg)
        create_input_player(self.ecs_world)
        self._ui_static_texts = create_interface_texts(self.ecs_world, self.interface_cfg)

    def _calculate_time(self):
        self.clock.tick(self.framerate)
        self.delta_time = self.clock.get_time() / 1000.0
        self.elapsed_time += self.delta_time

    def _process_events(self):
        for event in pygame.event.get():
            system_input_player(self.ecs_world, event, self._do_action)
            if event.type == pygame.QUIT:
                self.is_running = False

    def _update(self):
        if self._is_paused:
            self._update_ui_text()
            return

        system_enemy_spawner(self.ecs_world, self.delta_time)
        system_enemy_hunter_state(self.ecs_world, self._player_entity)
        system_player_state(self.ecs_world)

        system_movement(self.ecs_world, self.delta_time)

        system_screen_bounce(self.ecs_world, self.screen)
        system_screen_player(self.ecs_world, self.screen)
        system_screen_bullet(self.ecs_world, self.screen)

        system_collision_player_enemy(
            self.ecs_world, self._player_entity, self.level_cfg, self.explosion_cfg
        )
        system_collision_enemy_bullet(self.ecs_world, self.explosion_cfg)
        system_special_defense(
            self.ecs_world,
            self._player_entity,
            self.delta_time,
            self.explosion_cfg,
        )

        system_animation(self.ecs_world, self.delta_time)
        system_explosion_lifecycle(self.ecs_world)
        self.ecs_world._clear_dead_entities()
        self._sync_bullet_count()
        self._update_ui_text()

    def _draw(self):
        self.screen.fill(self.bg_color)
        system_rendering(self.ecs_world, self.screen)
        pygame.display.flip()

    def _clean(self):
        self.ecs_world.clear_database()
        pygame.quit()

    def _do_action(self, c_input: CInputCommand):
        if self._is_paused and c_input.name != "GAME_PAUSE":
            return

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
        elif c_input.name == "PLAYER_FIRE" and c_input.phase == CommandPhase.START:
            if (
                self._player_bullet_count
                < self.level_cfg["player_spawn"]["max_bullets"]
            ):
                spawn_player_bullet(
                    self.ecs_world,
                    self._player_c_t,
                    self._player_c_s,
                    self.bullet_cfg,
                )
                self._player_bullet_count += 1
        elif c_input.name == "GAME_PAUSE" and c_input.phase == CommandPhase.START:
            self._is_paused = not self._is_paused
        elif c_input.name == "PLAYER_SPECIAL" and c_input.phase == CommandPhase.START:
            special_defense = self.ecs_world.component_for_entity(
                self._player_entity, CPlayerSpecialDefense
            )
            if special_defense.try_activate():
                special_defense.shield_entity = create_special_defense_shield(
                    self.ecs_world,
                    self._player_c_t,
                    self._player_c_s,
                    self.shield_cfg,
                )
                ServiceLocator.sounds_service.play(special_defense.sound)

        self._handle_player_move_sound()

    def _handle_player_move_sound(self) -> None:
        is_moving = self._player_c_v.vel.magnitude_squared() > 0
        if is_moving and not self._is_player_moving:
            ServiceLocator.sounds_service.play(self.player_cfg["sound_move"])
        self._is_player_moving = is_moving

    def _update_ui_text(self) -> None:
        special_defense = self.ecs_world.component_for_entity(
            self._player_entity, CPlayerSpecialDefense
        )
        state = {
            "paused": self._is_paused,
            "special_active": special_defense.active_time_left,
            "special_cooldown": special_defense.cooldown_time_left,
            "bullets": self._player_bullet_count,
        }
        system_ui_text(self.ecs_world, state, self._ui_static_texts)

    def _sync_bullet_count(self) -> None:
        self._player_bullet_count = len(self.ecs_world.get_component(CTagBullet))
