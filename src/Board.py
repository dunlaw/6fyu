# Base on PropertyTycoonCardData.xlsx from canvas
# script based on Eric's provided flowchart photo (flowchart.drawio.png)
# This file contains the Board class, which is used to manage the board in the Property Tycoon game.

import pygame
import math
import os
from src.Property import Property
from typing import Optional, List
from src.Loadexcel import load_property_data
from src.Font_Manager import font_manager

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
UI_BG = (18, 18, 18)
ACCENT_COLOR = (75, 139, 190)
SUCCESS_COLOR = (40, 167, 69)
ERROR_COLOR = (220, 53, 69)

GROUP_COLORS = {
    "Brown": (102, 51, 0),
    "Blue": (0, 200, 255),
    "Purple": (128, 0, 128),
    "Orange": (255, 128, 0),
    "Red": (255, 0, 0),
    "Yellow": (255, 236, 93),
    "Green": (0, 153, 0),
    "Deep blue": (0, 0, 153),
    "Stations": (128, 128, 128),
    "Utilities": (192, 192, 192),
}


base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class CameraControls:
    def __init__(self):
        self.zoom_level = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.move_speed = 5
        self.zoom_speed = 0.05
        self.min_zoom = 0.5
        self.max_zoom = 2.0

    def handle_camera_controls(self, keys):
        if keys[pygame.K_PLUS] or keys[pygame.K_EQUALS]:
            self.zoom_level = min(self.max_zoom, self.zoom_level + self.zoom_speed)
        if keys[pygame.K_MINUS]:
            self.zoom_level = max(self.min_zoom, self.zoom_level - self.zoom_speed)

        adjusted_speed = self.move_speed * (1 / self.zoom_level)

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.offset_y -= adjusted_speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.offset_y += adjusted_speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.offset_x -= adjusted_speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.offset_x += adjusted_speed

        window_size = pygame.display.get_surface().get_size()
        max_offset = window_size[0] // 4
        self.offset_x = max(min(self.offset_x, max_offset), -max_offset)
        self.offset_y = max(min(self.offset_y, max_offset), -max_offset)

        return self.zoom_level, self.offset_x, self.offset_y


class Board:
    def __init__(self, players):
        self.players = players
        self.spaces = [None] * 40
        self.properties_data = load_property_data()
        self.camera = CameraControls()

        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        try:
            self.board_image = pygame.image.load(
                os.path.join(self.project_root, "assets/image/board.png")
            )
        except (pygame.error, FileNotFoundError) as e:
            print(f"Could not load board image: {e}")
            self.board_image = None

        try:
            self.original_background = pygame.image.load(
                os.path.join(self.project_root, "assets/image/background.jpg")
            )
            self.original_background = self.original_background.convert()
            self.background_image = self.original_background.copy()
        except (pygame.error, FileNotFoundError) as e:
            print(f"Could not load background image: {e}")
            self.original_background = None
            self.background_image = None

        self.board_rects = self._create_board_rects()
        self.messages = []
        self.message_times = []
        self.message_font = font_manager.get_font(15)
        self.price_font = font_manager.get_font(20)
        self.small_font = font_manager.get_font(14)

    def add_message(self, text):
        if text is None:
            return

        max_chars = 35

        if len(text) > max_chars:
            words = text.split()
            lines = []
            current_line = []

            for word in words:
                test_line = " ".join(current_line + [word])
                if len(test_line) <= max_chars:
                    current_line.append(word)
                else:
                    lines.append(" ".join(current_line))
                    current_line = [word]

            if current_line:
                lines.append(" ".join(current_line))

            for line in lines:
                self.messages.append(line)
                self.message_times.append(pygame.time.get_ticks())
        else:
            self.messages.append(text)
            self.message_times.append(pygame.time.get_ticks())

        while len(self.messages) > 9:
            self.messages.pop(0)
            self.message_times.pop(0)

    def _create_board_rects(self):
        screen_info = pygame.display.Info()
        window_width = screen_info.current_w
        window_height = screen_info.current_h
        base_board_size = min(window_width, window_height) * 0.8
        board_size = base_board_size * self.camera.zoom_level

        corner_size = board_size // 11
        normal_width = corner_size
        normal_height = int(normal_width * (5 / 8))

        start_x = ((window_width - board_size) // 2) + self.camera.offset_x
        start_y = ((window_height - board_size) // 2) + self.camera.offset_y

        rects = []

        for i in range(11):
            width = corner_size if (i == 0 or i == 10) else normal_width
            height = corner_size if (i == 0 or i == 10) else normal_height
            x = start_x
            y = start_y + board_size - height - (i * normal_width)
            rects.append(pygame.Rect(x, y, width, height))

        for i in range(11, 21):
            width = corner_size if i == 20 else normal_width
            height = corner_size if i == 20 else normal_height
            x = start_x + ((i - 10) * normal_width)
            y = start_y
            rects.append(pygame.Rect(x, y, width, height))

        for i in range(21, 31):
            width = corner_size if i == 30 else normal_height
            height = corner_size if i == 30 else normal_width
            x = start_x + board_size - width
            y = start_y + ((i - 20) * normal_width)
            rects.append(pygame.Rect(x, y, width, height))

        for i in range(31, 40):
            width = corner_size if i == 39 else normal_width
            height = corner_size if i == 39 else normal_height
            x = start_x + board_size - ((i - 29) * normal_width)
            y = start_y + board_size - height
            rects.append(pygame.Rect(x, y, width, height))

        return rects

    def update_board_positions(self):
        self.board_rects = self._create_board_rects()
        for player in self.players:
            if not isinstance(player.position, int) or not (1 <= player.position <= 40):
                print(
                    f"Warning: Invalid position {player.position} detected for {player.name} in update_board_positions, resetting to position 1"
                )
                player.position = 1

            player_rect = self.board_rects[player.position - 1]
            player.rect = player_rect

    def draw_player(self, screen, player, rect, index):
        is_corner = rect.width > rect.height + 10 or rect.height > rect.width + 10
        row = (player.player_number - 1) // 2
        col = (player.player_number - 1) % 2
        base_padding = 12 if is_corner else 8
        spacing = 35 if is_corner else 30

        if player.is_moving and player.current_path_index < len(player.move_path):
            if player.current_path_index == 0:
                start_rect = self.board_rects[player.move_start_position - 1]
                next_rect = self.board_rects[player.move_path[0] - 1]
            else:
                start_rect = self.board_rects[
                    player.move_path[player.current_path_index - 1] - 1
                ]
                next_rect = self.board_rects[
                    player.move_path[player.current_path_index] - 1
                ]

            progress = player.move_progress

            start_x, start_y = self._get_player_position_on_rect(
                start_rect, player.player_number, is_corner, False
            )
            target_x, target_y = self._get_player_position_on_rect(
                next_rect, player.player_number, is_corner, False
            )

            pos_x = int(start_x + (target_x - start_x) * progress)
            pos_y = int(start_y + (target_y - start_y) * progress)

            board_margin = 10
            pos_x = max(
                min(start_rect.x, next_rect.x) - board_margin,
                min(
                    pos_x,
                    max(start_rect.x + start_rect.width, next_rect.x + next_rect.width)
                    + board_margin,
                ),
            )
            pos_y = max(
                min(start_rect.y, next_rect.y) - board_margin,
                min(
                    pos_y,
                    max(
                        start_rect.y + start_rect.height, next_rect.y + next_rect.height
                    )
                    + board_margin,
                ),
            )

        else:
            if rect.width > rect.height + 10:
                pos_x = rect.x + base_padding + (col * spacing)
                pos_y = rect.y + (rect.height - 40) // 2 + (row * spacing // 2)
            elif rect.height > rect.width + 10:
                pos_x = rect.x + (rect.width - 40) // 2 + (col * spacing // 2)
                pos_y = rect.y + base_padding + (row * spacing)
            else:
                pos_x = rect.x + base_padding + (col * spacing)
                pos_y = rect.y + base_padding + (row * spacing)

            pos_x = max(rect.x + 2, min(pos_x, rect.x + rect.width - 42))
            pos_y = max(rect.y + 2, min(pos_y, rect.y + rect.height - 42))

        glow_surface = pygame.Surface((44, 44), pygame.SRCALPHA)
        for i in range(4):
            alpha = int(100 * (1 - i / 4))
            pygame.draw.rect(
                glow_surface,
                (*player.color[:3], alpha),
                pygame.Rect(i, i, 44 - i * 2, 44 - i * 2),
                border_radius=5,
            )
        screen.blit(glow_surface, (pos_x - 2, pos_y - 2 - player.animation_offset))

        if player.player_image:
            token_rect = pygame.Rect(pos_x, pos_y - player.animation_offset, 40, 40)
            screen.blit(player.player_image, token_rect)
        else:
            pygame.draw.circle(
                screen,
                player.color,
                (pos_x + 20, pos_y + 20 - player.animation_offset),
                20,
            )

    def _get_player_position_on_rect(
        self, rect, player_number, is_corner, apply_bounds=True
    ):
        row = (player_number - 1) // 2
        col = (player_number - 1) % 2
        base_padding = 12 if is_corner else 8
        spacing = 35 if is_corner else 30

        if rect.width > rect.height + 10:
            pos_x = rect.x + base_padding + (col * spacing)
            pos_y = rect.y + (rect.height - 40) // 2 + (row * spacing // 2)
        elif rect.height > rect.width + 10:
            pos_x = rect.x + (rect.width - 40) // 2 + (col * spacing // 2)
            pos_y = rect.y + base_padding + (row * spacing)
        else:
            pos_x = rect.x + base_padding + (col * spacing)
            pos_y = rect.y + base_padding + (row * spacing)

        if apply_bounds:
            pos_x = max(rect.x + 2, min(pos_x, rect.x + rect.width - 42))
            pos_y = max(rect.y + 2, min(pos_y, rect.y + rect.height - 42))

        return pos_x, pos_y

    def draw(self, screen):
        window_width = screen.get_width()
        window_height = screen.get_height()
        base_board_size = int(window_height * 0.9)
        board_size = int(base_board_size * self.camera.zoom_level)
        board_size = max(1, board_size)

        game_surface = pygame.Surface((window_width, window_height))
        game_surface.fill(WHITE)

        if self.original_background:
            bg_width, bg_height = self.original_background.get_size()
            bg_aspect = bg_width / bg_height
            window_aspect = window_width / window_height

            if window_aspect > bg_aspect:
                scaled_width = window_width
                scaled_height = int(scaled_width / bg_aspect)
            else:
                scaled_height = window_height
                scaled_width = int(scaled_height * bg_aspect)

            pos_x = (window_width - scaled_width) // 2
            pos_y = (window_height - scaled_height) // 2

            scaled_bg = pygame.transform.scale(
                self.original_background, (scaled_width, scaled_height)
            )
            game_surface.blit(scaled_bg, (pos_x, pos_y))
        else:
            game_surface.fill(UI_BG)

        keys = pygame.key.get_pressed()
        zoom, offset_x, offset_y = self.camera.handle_camera_controls(keys)
        self.camera.zoom_level = zoom
        self.camera.offset_x = offset_x
        self.camera.offset_y = offset_y

        self.update_board_positions()

        board_x = ((window_width - board_size) // 2) + self.camera.offset_x
        board_y = ((window_height - board_size) // 2) + self.camera.offset_y

        board_surface = pygame.Surface((board_size, board_size))
        board_surface.fill(WHITE)
        if self.board_image:
            scaled_board = pygame.transform.smoothscale(
                self.board_image, (board_size, board_size)
            )
            board_surface.blit(scaled_board, (0, 0))
        game_surface.blit(board_surface, (board_x, board_y))

        transparent_surface = pygame.Surface(
            (window_width, window_height), pygame.SRCALPHA
        )

        for player in self.players:
            if not isinstance(player.position, int) or not (1 <= player.position <= 40):
                print(
                    f"Warning: Invalid position {player.position} detected for {player.name} in draw, resetting to position 1"
                )
                player.position = 1

            if player.is_moving and player.current_path_index < len(player.move_path):
                rect_for_animation = None

                if player.current_path_index == 0:
                    start_pos = player.move_start_position - 1
                    end_pos = player.move_path[0] - 1
                else:
                    start_pos = player.move_path[player.current_path_index - 1] - 1
                    end_pos = player.move_path[player.current_path_index] - 1

                start_pos = max(0, min(start_pos, len(self.board_rects) - 1))
                end_pos = max(0, min(end_pos, len(self.board_rects) - 1))

                if 0 <= start_pos < len(self.board_rects) and 0 <= end_pos < len(
                    self.board_rects
                ):
                    rect_for_animation = self.board_rects[start_pos]
                    is_corner = (
                        rect_for_animation.width > rect_for_animation.height + 10
                        or rect_for_animation.height > rect_for_animation.width + 10
                    )
                    self.draw_player(
                        transparent_surface,
                        player,
                        rect_for_animation,
                        player.player_number,
                    )
            else:
                pos_index = max(0, min(player.position - 1, len(self.board_rects) - 1))
                player_rect = self.board_rects[pos_index]
                self.draw_player(
                    transparent_surface, player, player_rect, player.player_number
                )

        info_panel_width = 290
        info_panel_height = 230
        info_panel_x = 20
        info_panel_y = window_height - info_panel_height - 20

        shadow_depth = 6
        panel_shadow = pygame.Surface(
            (info_panel_width + shadow_depth * 2, info_panel_height + shadow_depth * 2),
            pygame.SRCALPHA,
        )
        for i in range(shadow_depth):
            alpha = int(120 * (1 - i / shadow_depth))
            pygame.draw.rect(
                panel_shadow,
                (*BLACK, alpha),
                pygame.Rect(
                    i,
                    i,
                    info_panel_width + shadow_depth * 2 - i * 2,
                    info_panel_height + shadow_depth * 2 - i * 2,
                ),
                border_radius=12,
            )
        transparent_surface.blit(
            panel_shadow, (info_panel_x - shadow_depth, info_panel_y - shadow_depth)
        )

        info_panel = pygame.Surface(
            (info_panel_width, info_panel_height), pygame.SRCALPHA
        )

        pygame.draw.rect(
            info_panel, (*UI_BG, 230), info_panel.get_rect(), border_radius=10
        )

        header_height = 30
        header_rect = pygame.Rect(0, 0, info_panel_width, header_height)
        pygame.draw.rect(info_panel, ACCENT_COLOR, header_rect, border_radius=10)
        pygame.draw.rect(
            info_panel,
            ACCENT_COLOR,
            pygame.Rect(0, header_height - 10, info_panel_width, 10),
        )

        title_font = font_manager.get_font(20)
        title_text = title_font.render("MESSAGE LOG", True, WHITE)
        title_rect = title_text.get_rect(
            center=(info_panel_width // 2, header_height // 2)
        )
        info_panel.blit(title_text, title_rect)

        border_width = 2
        pygame.draw.rect(
            info_panel, WHITE, info_panel.get_rect(), border_width, border_radius=10
        )

        transparent_surface.blit(info_panel, (info_panel_x, info_panel_y))

        line_height = self.message_font.get_height() + 5
        max_messages = (info_panel_height - header_height - 20) // line_height
        visible_messages = self.messages[-max_messages:]
        text_y = info_panel_y + header_height + 10

        for message in visible_messages:
            text = self.message_font.render(message, True, WHITE)
            transparent_surface.blit(text, (info_panel_x + 15, text_y))
            text_y += line_height

        game_surface.blit(transparent_surface, (0, 0))
        screen.blit(game_surface, (0, 0))

    def get_space(self, position):
        array_pos = (position - 1) % 40
        if array_pos <= 9:
            mapped_pos = array_pos
        elif array_pos <= 19:
            mapped_pos = array_pos
        elif array_pos <= 29:
            mapped_pos = array_pos
        else:
            mapped_pos = array_pos

        if 0 <= mapped_pos < len(self.spaces):
            return self.spaces[mapped_pos]
        return None

    def update_ownership(self, properties_data):
        for position_str, prop_data in properties_data.items():
            try:
                position = int(position_str)
                array_pos = position - 1
                if 0 <= array_pos < 40 and self.spaces[array_pos]:
                    self.spaces[array_pos].owner = prop_data.get("owner")
            except (ValueError, TypeError) as e:
                print(f"Error updating ownership for position {position_str}: {e}")

        self.properties_data.update(properties_data)

    def get_property_group(self, position):
        if str(position) in self.properties_data:
            return self.properties_data[str(position)].get("group")
        return None

    def get_property_position(self, position):
        if not 1 <= position <= 40:
            return None

        pos_index = position - 1
        if pos_index < len(self.board_rects):
            rect = self.board_rects[pos_index]
            return (rect.x + rect.width // 2, rect.y + rect.height // 2)
        return None

    def board_to_screen(self, x, y):
        return (x, y)

    def update_offset(self, dx, dy):
        self.camera.offset_x += dx
        self.camera.offset_y += dy

        window_size = pygame.display.get_surface().get_size()
        max_offset = window_size[0] // 4
        self.camera.offset_x = max(min(self.camera.offset_x, max_offset), -max_offset)
        self.camera.offset_y = max(min(self.camera.offset_y, max_offset), -max_offset)

        self.update_board_positions()

    def property_clicked(self, pos):
        for i, rect in enumerate(self.board_rects):
            expanded_rect = rect.inflate(10, 10)
            if expanded_rect.collidepoint(pos):
                return i + 1
        return None
