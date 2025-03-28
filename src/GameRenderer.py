# Property Tycoon GameRenderer.py
# It contains the classes for the game renderer, such as the draw functions, the draw buttons, and the draw time remaining.

import pygame
import math
import os
from src.Font_Manager import font_manager
from src.UI import DevelopmentNotification, AIEmotionUI

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
UI_BG = (18, 18, 18)

DARK_RED = (139, 0, 0)
DARK_GREEN = (0, 100, 0)
DARK_BLUE = (0, 0, 139)
GOLD = (218, 165, 32)
CREAM = (255, 253, 208)
BURGUNDY = (128, 0, 32)

RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

ACCENT_COLOR = BURGUNDY
BUTTON_HOVER = (160, 20, 40)
ERROR_COLOR = (220, 53, 69)
SUCCESS_COLOR = DARK_GREEN
MODE_COLOR = DARK_BLUE
TIME_COLOR = (255, 180, 100)
HUMAN_COLOR = DARK_GREEN
AI_COLOR = DARK_RED

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


class GameRenderer:
    def __init__(self, game, game_actions):
        self.game = game
        self.game_actions = game_actions
        self.screen = game.screen
        self.font = game.font
        self.small_font = game.small_font
        self.tiny_font = game.tiny_font
        self.button_font = game.button_font
        self.message_font = game.message_font

    def draw_button(self, button, text, hover=False, active=True):
        if not active:
            base_color = GRAY
        else:
            base_color = BUTTON_HOVER if hover else ACCENT_COLOR

        shadow_rect = button.copy()
        shadow_rect.y += 4
        shadow = pygame.Surface(button.size, pygame.SRCALPHA)
        pygame.draw.rect(shadow, (*BLACK, 128), shadow.get_rect(), border_radius=8)
        self.screen.blit(shadow, shadow_rect)

        button_surface = pygame.Surface(button.size, pygame.SRCALPHA)

        gradient = pygame.Surface(button.size, pygame.SRCALPHA)
        for i in range(button.height):
            alpha = 255 - int(i * 0.5)
            pygame.draw.line(gradient, (*base_color, alpha), (0, i), (button.width, i))

        pygame.draw.rect(
            button_surface, base_color, button_surface.get_rect(), border_radius=8
        )
        button_surface.blit(gradient, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        border_color = GOLD if hover else CREAM
        pygame.draw.rect(
            button_surface,
            border_color,
            button_surface.get_rect(),
            width=2,
            border_radius=8,
        )

        if hover:
            highlight = pygame.Surface(button.size, pygame.SRCALPHA)
            for i in range(4):
                alpha = 100 - i * 25
                pygame.draw.rect(
                    highlight,
                    (255, 255, 255, alpha),
                    highlight.get_rect().inflate(-i * 2, -i * 2),
                    border_radius=8,
                )
            button_surface.blit(highlight, (0, 0))

        self.screen.blit(button_surface, button)

        text_shadow = self.font.render(text, True, BLACK)
        text_rect_shadow = text_shadow.get_rect(center=button.center)
        text_rect_shadow.x += 1
        text_rect_shadow.y += 1
        self.screen.blit(text_shadow, text_rect_shadow)

        text_surface = self.font.render(text, True, CREAM)
        text_rect = text_surface.get_rect(center=button.center)
        self.screen.blit(text_surface, text_rect)

    def draw_time_remaining(self):
        if self.game.game_mode == "abridged" and self.game.time_limit:
            current_time = pygame.time.get_ticks()

            elapsed = (
                current_time - self.game.start_time - self.game.total_pause_time
            ) // 1000

            if self.game.game_paused:
                current_pause_duration = current_time - self.game.pause_start_time
                elapsed = (
                    current_time
                    - self.game.start_time
                    - self.game.total_pause_time
                    - current_pause_duration
                ) // 1000

            remaining = max(0, self.game.time_limit - elapsed)
            minutes = remaining // 60
            seconds = remaining % 60

            window_size = self.screen.get_size()

            if remaining <= 30 and not hasattr(self.game, "time_limit_reached"):
                warning_intensity = (30 - remaining) / 30

                flash_value = abs(math.sin(current_time / 300))
                pulse_intensity = 0.4 + (flash_value * 0.6 * warning_intensity)

                border_width = int(20 + (30 * warning_intensity * flash_value))

                border_color = (255, 0, 0, int(180 * pulse_intensity))

                warning_surface = pygame.Surface(window_size, pygame.SRCALPHA)

                pygame.draw.rect(
                    warning_surface, border_color, (0, 0, window_size[0], border_width)
                )

                pygame.draw.rect(
                    warning_surface,
                    border_color,
                    (0, window_size[1] - border_width, window_size[0], border_width),
                )

                pygame.draw.rect(
                    warning_surface,
                    border_color,
                    (
                        0,
                        border_width,
                        border_width,
                        window_size[1] - (2 * border_width),
                    ),
                )

                pygame.draw.rect(
                    warning_surface,
                    border_color,
                    (
                        window_size[0] - border_width,
                        border_width,
                        border_width,
                        window_size[1] - (2 * border_width),
                    ),
                )

                self.screen.blit(warning_surface, (0, 0))

                if remaining <= 10:
                    overlay_intensity = int(25 * (10 - remaining) / 10 * flash_value)
                    overlay = pygame.Surface(window_size, pygame.SRCALPHA)
                    overlay.fill((255, 0, 0, overlay_intensity))
                    self.screen.blit(overlay, (0, 0))

            if (
                hasattr(self.game, "time_limit_reached")
                and self.game.time_limit_reached
                and not self.game.game_over
            ):
                banner_height = 40
                banner_surface = pygame.Surface(
                    (window_size[0], banner_height), pygame.SRCALPHA
                )
                banner_color = (255, 0, 0, 150)
                banner_surface.fill(banner_color)
                self.screen.blit(banner_surface, (0, 0))

                font = pygame.font.Font(None, 28)
                text = font.render(
                    "TIME'S UP! Finishing current lap...", True, (255, 255, 255)
                )
                text_rect = text.get_rect(
                    center=(window_size[0] // 2, banner_height // 2)
                )
                self.screen.blit(text, text_rect)

                remaining = 0
                minutes = 0
                seconds = 0

            if remaining <= self.game.time_warning_start:
                flash_alpha = (
                    abs(math.sin(current_time / self.game.warning_flash_rate)) * 255
                )
                warning_surface = pygame.Surface(window_size, pygame.SRCALPHA)
                warning_color = (*ERROR_COLOR, int(flash_alpha * 0.1))
                warning_surface.fill(warning_color)
                self.screen.blit(warning_surface, (0, 0))

                if remaining == 60 or remaining == 30 or remaining == 10:
                    self.game.add_message(f"Warning: {remaining} seconds remaining!")

            panel_width = 200
            panel_height = 120
            panel_x = 10
            panel_y = 70

            glow_surface = pygame.Surface(
                (panel_width + 10, panel_height + 10), pygame.SRCALPHA
            )
            for i in range(5):
                alpha = int(100 * (1 - i / 5))
                pygame.draw.rect(
                    glow_surface,
                    (*ACCENT_COLOR[:3], alpha),
                    pygame.Rect(
                        i, i, panel_width + 10 - i * 2, panel_height + 10 - i * 2
                    ),
                    border_radius=10,
                )
            self.screen.blit(glow_surface, (panel_x - 5, panel_y - 5))

            panel = pygame.Surface((panel_width, panel_height))
            panel.fill(UI_BG)
            self.screen.blit(panel, (panel_x, panel_y))

            panel_title = self.small_font.render("GAME STATUS", True, LIGHT_GRAY)
            panel_title_rect = panel_title.get_rect(
                centerx=panel_x + panel_width // 2, top=panel_y + 10
            )
            self.screen.blit(panel_title, panel_title_rect)

            active_players = [
                p["name"] for p in self.game.logic.players if not p.get("exited", False)
            ]
            min_lap = (
                min([self.game.lap_count[p] for p in active_players])
                if active_players
                else 0
            )

            time_color = ERROR_COLOR if remaining < 300 else ACCENT_COLOR

            lap_y = panel_title_rect.bottom + 7
            lap_icon_text = "🏁"
            lap_icon = self.small_font.render(lap_icon_text, True, LIGHT_GRAY)
            self.screen.blit(lap_icon, (panel_x + 15, lap_y))

            lap_text = self.font.render(f"Lap {min_lap}", True, ACCENT_COLOR)
            self.screen.blit(lap_text, (panel_x + 40, lap_y - 5))

            time_y = lap_y + 25
            time_icon_text = "⏱️"
            time_icon = self.small_font.render(time_icon_text, True, LIGHT_GRAY)
            self.screen.blit(time_icon, (panel_x + 15, time_y))

            time_text = self.font.render(
                f"{minutes:02d}:{seconds:02d}", True, time_color
            )
            self.screen.blit(time_text, (panel_x + 40, time_y - 5))

            progress_width = panel_width - 30
            progress_height = 8
            progress_x = panel_x + 15
            progress_y = panel_y + panel_height - 20

            progress_percent = 1 - (remaining / self.game.time_limit)

            pygame.draw.rect(
                self.screen,
                GRAY,
                pygame.Rect(progress_x, progress_y, progress_width, progress_height),
                border_radius=4,
            )

            fill_width = int(progress_width * progress_percent)
            fill_color = ERROR_COLOR if remaining < 300 else ACCENT_COLOR
            if fill_width > 0:
                pygame.draw.rect(
                    self.screen,
                    fill_color,
                    pygame.Rect(progress_x, progress_y, fill_width, progress_height),
                    border_radius=4,
                )

    def draw(self):
        if self.game.game_mode == "abridged" and self.game.check_time_limit():
            return

        if not pygame.display.get_surface():
            return

        window_size = self.screen.get_size()
        self.screen.fill(UI_BG)
        gradient = pygame.Surface(window_size, pygame.SRCALPHA)
        for i in range(window_size[1]):
            alpha = int(255 * (1 - i / window_size[1]))
            pygame.draw.line(
                gradient, (*ACCENT_COLOR[:3], alpha), (0, i), (window_size[0], i)
            )
        self.screen.blit(gradient, (0, 0))

        if self.game.state == "DEVELOPMENT" and self.game.dev_manager.is_active:
            self.game.dev_manager.draw(pygame.mouse.get_pos())

        self.game.board.draw(self.screen)

        if self.game.development_mode:
            self.game.dev_manager.draw(pygame.mouse.get_pos())

        for emotion_ui in self.game.emotion_uis.values():
            emotion_ui.draw()

        self.game.synchronize_player_positions()
        self.game.synchronize_player_money()
        self.game.synchronize_free_parking_pot()

        for player in self.game.players:
            player.update_animation()

            if (
                hasattr(player, "prev_moving")
                and player.prev_moving
                and not player.is_moving
            ):
                self.game.check_passing_go(player, player.move_start_position)
            player.prev_moving = player.is_moving

        any_player_moving = any(player.is_moving for player in self.game.players)

        if (
            hasattr(self.game, "waiting_for_animation")
            and self.game.waiting_for_animation
            and not any_player_moving
        ):
            self.game.waiting_for_animation = False

            if (
                hasattr(self.game, "pending_auction_property")
                and self.game.pending_auction_property
            ):
                print("Animations completed - starting pending auction")
                property_data = self.game.pending_auction_property
                self.game.pending_auction_property = None
                self.game_actions.start_auction(property_data)

        if hasattr(self.game, "auction_completed") and self.game.auction_completed:
            current_time = pygame.time.get_ticks()
            if current_time - self.game.auction_end_time > self.game.auction_end_delay:
                print("Auction delay timer elapsed - changing state to ROLL")
                self.game.state = "ROLL"
                self.game.auction_completed = False

        self.game.board.draw(self.screen)

        mouse_pos = pygame.mouse.get_pos()

        panel_width = 280
        panel_spacing = 10
        player_height = 100
        total_height = (player_height + panel_spacing) * len(
            self.game.logic.players
        ) - panel_spacing
        panel_x = window_size[0] - panel_width - 20
        panel_y = 20

        panel_surface = pygame.Surface((panel_width, total_height), pygame.SRCALPHA)
        pygame.draw.rect(
            panel_surface, (0, 0, 0, 180), panel_surface.get_rect(), border_radius=15
        )
        self.screen.blit(panel_surface, (panel_x, panel_y))

        current_y = panel_y
        hovered_property = None

        for i, player_data in enumerate(self.game.logic.players):
            is_current = i == self.game.logic.current_player_index
            player_obj = next(
                (p for p in self.game.players if p.name == player_data["name"]), None
            )

            player_rect = pygame.Rect(panel_x, current_y, panel_width, player_height)

            if is_current:
                highlight_surface = pygame.Surface(
                    (panel_width, player_height), pygame.SRCALPHA
                )
                highlight_color = (*ACCENT_COLOR[:3], 50)
                pygame.draw.rect(
                    highlight_surface,
                    highlight_color,
                    highlight_surface.get_rect(),
                    border_radius=15,
                )
                self.screen.blit(highlight_surface, player_rect)

            logo_size = 50
            logo_margin = 8
            logo_rect = pygame.Rect(
                panel_x + logo_margin,
                current_y + (player_height - logo_size) // 2,
                logo_size,
                logo_size,
            )

            if player_obj and player_obj.player_image:
                scaled_logo = pygame.transform.scale(
                    player_obj.player_image, (logo_size, logo_size)
                )
                if (
                    player_data.get("exited", False)
                    or player_data.get("bankrupt", False)
                    or (
                        player_obj
                        and (player_obj.voluntary_exit or player_obj.bankrupt)
                    )
                ):
                    scaled_logo.set_alpha(128)
                self.screen.blit(scaled_logo, logo_rect)

            info_x = logo_rect.right + 10
            info_y = current_y + 10

            name_color = ACCENT_COLOR if is_current else WHITE
            if player_data.get("in_jail", False):
                name_text = f"{player_data['name']} [JAIL]"
                name_color = ERROR_COLOR if is_current else GRAY
            elif player_data.get("exited", False) or (
                player_obj and player_obj.voluntary_exit
            ):
                name_text = player_data["name"]
                name_color = (200, 0, 0)
            elif player_data.get("bankrupt", False) or (
                player_obj and player_obj.bankrupt
            ):
                name_text = player_data["name"]
                name_color = (200, 0, 0)
            else:
                name_text = player_data["name"]

            name_surface = self.font.render(name_text, True, name_color)
            self.screen.blit(name_surface, (info_x, info_y))

            if player_data.get("exited", False) or (
                player_obj and player_obj.voluntary_exit
            ):
                exit_text = self.small_font.render("[EXITED]", True, (200, 0, 0))
                self.screen.blit(
                    exit_text, (info_x, info_y + name_surface.get_height())
                )
            elif player_data.get("bankrupt", False) or (
                player_obj and player_obj.bankrupt
            ):
                bankrupt_text = self.small_font.render("[BANKRUPT]", True, (200, 0, 0))
                self.screen.blit(
                    bankrupt_text, (info_x, info_y + name_surface.get_height())
                )

            money_y = info_y + 30
            if (
                player_data.get("exited", False)
                or player_data.get("bankrupt", False)
                or (player_obj and (player_obj.voluntary_exit or player_obj.bankrupt))
            ):
                money_y += 15

            money_text = f"£ {player_data['money']:,}"
            money_color = (
                SUCCESS_COLOR
                if player_data["money"] > 500
                else ERROR_COLOR if player_data["money"] < 200 else WHITE
            )
            money_surface = self.small_font.render(money_text, True, money_color)
            self.screen.blit(money_surface, (info_x, money_y))

            props = [
                prop
                for prop in self.game.logic.properties.values()
                if prop.get("owner") == player_data["name"]
            ]

            if props:
                prop_x = info_x
                prop_y = money_y + 30
                prop_size = 15
                prop_spacing = 5
                max_props_per_row = 6

                for idx, prop in enumerate(props):
                    row = idx // max_props_per_row
                    col = idx % max_props_per_row
                    x = prop_x + col * (prop_size + prop_spacing)
                    y = prop_y + row * (prop_size + prop_spacing)

                    prop_rect = pygame.Rect(x, y, prop_size, prop_size)
                    group = prop.get("group")
                    color = GROUP_COLORS.get(group, GRAY) if group else GRAY

                    pygame.draw.rect(self.screen, color, prop_rect, border_radius=3)

                    houses = prop.get("houses", 0)
                    if houses > 0:
                        if houses == 5:
                            indicator_color = RED
                            indicator_text = "H"
                        else:
                            indicator_color = GREEN
                            indicator_text = str(houses)

                        indicator_surface = self.tiny_font.render(
                            indicator_text, True, WHITE
                        )
                        indicator_rect = indicator_surface.get_rect(
                            center=prop_rect.center
                        )

                        self.screen.blit(indicator_surface, indicator_rect)

                    if prop_rect.collidepoint(mouse_pos):
                        hovered_property = prop
                        pygame.draw.rect(
                            self.screen, WHITE, prop_rect, 1, border_radius=3
                        )

            if i < len(self.game.logic.players) - 1:
                pygame.draw.line(
                    self.screen,
                    GRAY,
                    (panel_x + 10, current_y + player_height - 1),
                    (panel_x + panel_width - 10, current_y + player_height - 1),
                )

            current_y += player_height + panel_spacing

        if hovered_property:
            self.draw_property_tooltip(hovered_property, mouse_pos)

        self.draw_time_remaining()

        self.draw_free_parking_pot()

        self.draw_notification()

        for emotion_ui in self.game.emotion_uis.values():
            emotion_ui.draw()

        if self.game.state == "ROLL":
            current_player = next(
                (
                    p
                    for p in self.game.players
                    if p.name
                    == self.game.logic.players[self.game.logic.current_player_index][
                        "name"
                    ]
                ),
                None,
            )
            self.game.current_player_is_ai = current_player and current_player.is_ai

            human_players_remaining = any(
                not p.is_ai and not p.voluntary_exit and not p.bankrupt
                for p in self.game.players
            )

            if not self.game.current_player_is_ai:
                for emotion_ui in self.game.emotion_uis.values():
                    emotion_ui.draw()

                if not self.game.development_mode:
                    self.draw_button(
                        self.game.roll_button,
                        "Roll",
                        hover=self.game.roll_button.collidepoint(mouse_pos),
                    )

                if self.game.game_mode == "abridged" and self.game.time_limit:
                    pause_hover = self.game.pause_button.collidepoint(mouse_pos)
                    button_text = "Continue" if self.game.game_paused else "Pause"
                    self.draw_button(
                        self.game.pause_button, button_text, hover=pause_hover
                    )

                if human_players_remaining:
                    quit_hover = self.game.quit_button.collidepoint(mouse_pos)
                    base_color = BUTTON_HOVER if quit_hover else ERROR_COLOR

                    shadow_rect = self.game.quit_button.copy()
                    shadow_rect.y += 2
                    shadow = pygame.Surface(self.game.quit_button.size, pygame.SRCALPHA)
                    pygame.draw.rect(
                        shadow, (*BLACK, 128), shadow.get_rect(), border_radius=5
                    )
                    self.screen.blit(shadow, shadow_rect)

                    pygame.draw.rect(
                        self.screen, base_color, self.game.quit_button, border_radius=5
                    )
                    gradient = pygame.Surface(
                        self.game.quit_button.size, pygame.SRCALPHA
                    )
                    for i in range(self.game.quit_button.height):
                        alpha = int(100 * (1 - i / self.game.quit_button.height))
                        pygame.draw.line(
                            gradient,
                            (255, 255, 255, alpha),
                            (0, i),
                            (self.game.quit_button.width, i),
                        )
                    self.screen.blit(gradient, self.game.quit_button)

                    quit_text = self.font.render("Leave", True, WHITE)
                    text_rect = quit_text.get_rect(center=self.game.quit_button.center)
                    text_shadow = self.font.render("Leave", True, BLACK)
                    text_shadow_rect = text_shadow.get_rect(
                        center=self.game.quit_button.center
                    )
                    text_shadow_rect.x += 1
                    text_shadow_rect.y += 1
                    self.screen.blit(text_shadow, text_shadow_rect)
                    self.screen.blit(quit_text, text_rect)

            elif not self.game.dice_animation and not any_player_moving:
                self.game.check_and_trigger_ai_turn()

        elif self.game.state == "BUY" and self.game.current_property is not None:
            self.draw_property_card(self.game.current_property)
            self.draw_buy_options(mouse_pos)
        elif self.game.state == "AUCTION" and hasattr(
            self.game.logic, "current_auction"
        ):
            if self.game.logic.current_auction is None and not hasattr(
                self.game, "auction_completed"
            ):
                print(
                    "Warning: current_auction is None and no completion in progress - resetting state to ROLL"
                )
                self.game.state = "ROLL"
                return

            if self.game.logic.current_auction:
                self.draw_auction(self.game.logic.current_auction)
                result_message = self.game.logic.check_auction_end()
                if result_message == "auction_completed":
                    print("Auction completed in draw method - setting up delay")

                    if (
                        self.game.logic.current_auction
                        and self.game.logic.current_auction.get("highest_bidder")
                    ):
                        winner = self.game.logic.current_auction["highest_bidder"]
                        property_name = self.game.logic.current_auction.get(
                            "property", {}
                        ).get("name", "Unknown property")
                        bid_amount = self.game.logic.current_auction.get(
                            "current_bid", 0
                        )
                        self.game.board.add_message(
                            f"{winner['name']} won {property_name} for £{bid_amount}"
                        )
                    else:
                        property_name = self.game.logic.current_auction.get(
                            "property", {}
                        ).get("name", "Unknown property")
                        self.game.board.add_message(f"No one bid on {property_name}")

                    self.game.auction_end_time = pygame.time.get_ticks()
                    self.game.auction_end_delay = 3000
                    self.game.auction_completed = True
                    self.game.board.update_ownership(self.game.logic.properties)
        elif (
            self.game.state == "DEVELOPMENT" and self.game.selected_property is not None
        ):
            if (
                hasattr(self.game.logic, "current_auction")
                and self.game.logic.current_auction
            ):
                print("Auction in progress - not showing development UI")
            else:
                current_player = self.game.logic.players[
                    self.game.logic.current_player_index
                ]
                player_obj = next(
                    (p for p in self.game.players if p.name == current_player["name"]),
                    None,
                )

                if player_obj and player_obj.is_ai:
                    print(
                        f"Auto-closing development UI for AI player {current_player['name']}"
                    )
                    self.game.state = "ROLL"
                    self.game.selected_property = None
                    self.game.development_mode = False
                elif current_player.get("in_jail", False):
                    print(
                        f"Player {current_player['name']} is in jail - not showing development UI"
                    )
                    self.game.state = "ROLL"
                    self.game.selected_property = None
                    self.game.development_mode = False
                else:
                    self.draw_development_ui(self.game.selected_property)

        if (
            self.game.development_mode
            and not any_player_moving
            and not self.game.dice_animation
        ):
            if self.game.state in ["BUY", "AUCTION"]:
                return

            if (
                hasattr(self.game.logic, "current_auction")
                and self.game.logic.current_auction
            ):
                print("Auction in progress - not showing development notification")
            else:
                current_player = self.game.logic.players[
                    self.game.logic.current_player_index
                ]
                owned_properties = [
                    p
                    for p in self.game.logic.properties.values()
                    if p.get("owner") == current_player["name"]
                ]
                if owned_properties:
                    if not self.game.dev_notification:
                        self.game.dev_notification = DevelopmentNotification(
                            self.screen, current_player["name"], self.font
                        )

                    self.game.dev_notification.draw(mouse_pos)

        current_time = pygame.time.get_ticks()
        if self.game.dice_animation:
            if current_time - self.game.animation_start < self.game.animation_duration:
                dice1 = ((current_time // 100) % 6) + 1
                dice2 = ((current_time // 150) % 6) + 1
                self.draw_dice(dice1, dice2, True)
            else:
                self.game.finish_dice_animation()
        elif self.game.last_roll and (
            current_time - self.game.roll_time < self.game.ROLL_DISPLAY_TIME
        ):
            dice1, dice2 = self.game.last_roll
            self.draw_dice(dice1, dice2, False)

        if (
            self.game.show_card
            and self.game.current_card
            and self.game.current_card_player
        ):
            self.draw_card_alert(self.game.current_card, self.game.current_card_player)

            if (
                current_time - self.game.card_display_time
                > self.game.CARD_DISPLAY_DURATION
            ):
                self.game.show_card = False
                self.game.current_card = None
                self.game.current_card_player = None

        self.game.board.camera.handle_camera_controls(pygame.key.get_pressed())

        self.game.board.update_board_positions()

        if not self.game.game_over:
            game_over_data = self.game.check_game_over()
            if game_over_data:
                if "winner" in game_over_data:
                    self.game.handle_game_over(game_over_data["winner"])

        if self.game.show_popup:
            self.draw_popup_message()

        pygame.display.flip()

    def draw_dice(self, dice1, dice2, is_rolling):
        window_size = self.screen.get_size()
        dice_size = int(window_size[1] * 0.08)
        spacing = dice_size // 3
        start_x = window_size[0] - (dice_size * 2 + spacing) - 20
        y = window_size[1] - dice_size - 80

        for i, value in enumerate([dice1, dice2]):
            x = start_x + (dice_size + spacing) * i

            shadow_rect = pygame.Rect(x + 2, y + 2, dice_size, dice_size)
            shadow = pygame.Surface((dice_size, dice_size), pygame.SRCALPHA)
            pygame.draw.rect(shadow, (*BLACK, 128), shadow.get_rect(), border_radius=10)
            self.screen.blit(shadow, shadow_rect)

            dice_rect = pygame.Rect(x, y, dice_size, dice_size)
            pygame.draw.rect(self.screen, WHITE, dice_rect, border_radius=10)

            if value in self.game.dice_images:
                scaled_dice = pygame.transform.scale(
                    self.game.dice_images[value], (dice_size - 4, dice_size - 4)
                )
                image_rect = scaled_dice.get_rect(center=dice_rect.center)
                self.screen.blit(scaled_dice, image_rect)
            else:
                dice_text = self.font.render(str(value), True, BLACK)
                dice_text_rect = dice_text.get_rect(center=dice_rect.center)
                self.screen.blit(dice_text, dice_text_rect)

            color = ACCENT_COLOR if is_rolling else BLACK
            pygame.draw.rect(self.screen, color, dice_rect, 2, border_radius=10)

        if not is_rolling and dice1 == dice2:
            current_time = pygame.time.get_ticks()
            num_sparkles = 20
            for i in range(num_sparkles):
                angle = (current_time / 500 + i * (360 / num_sparkles)) % 360
                radius = 40 + math.sin(current_time / 200 + i) * 10
                sparkle_x = (
                    start_x
                    + dice_size
                    + spacing / 2
                    + math.cos(math.radians(angle)) * radius
                )
                sparkle_y = y + dice_size / 2 + math.sin(math.radians(angle)) * radius
                sparkle_color = (
                    255,
                    255,
                    0,
                    max(0, math.sin(current_time / 200 + i) * 255),
                )
                sparkle_surface = pygame.Surface((4, 4), pygame.SRCALPHA)
                pygame.draw.circle(sparkle_surface, sparkle_color, (2, 2), 2)
                self.screen.blit(sparkle_surface, (sparkle_x, sparkle_y))

    def draw_property_card(self, property_data):
        if not property_data:
            return

        window_size = self.screen.get_size()
        card_width = int(window_size[0] * 0.25)
        card_height = int(window_size[1] * 0.4)
        card_x = (window_size[0] - card_width) // 2
        card_y = (window_size[1] - card_height) // 2

        shadow_rect = pygame.Rect(card_x + 4, card_y + 4, card_width, card_height)
        shadow = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (*BLACK, 128), shadow.get_rect(), border_radius=15)
        self.screen.blit(shadow, shadow_rect)

        card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
        pygame.draw.rect(self.screen, WHITE, card_rect, border_radius=15)

        if "group" in property_data:
            header_height = 40
            header_rect = pygame.Rect(card_x, card_y, card_width, header_height)
            header_color = GROUP_COLORS.get(property_data["group"], GRAY)
            pygame.draw.rect(self.screen, header_color, header_rect, border_radius=15)
            pygame.draw.rect(
                self.screen,
                header_color,
                pygame.Rect(card_x, card_y + header_height - 15, card_width, 15),
            )

        name_text = self.font.render(property_data["name"], True, BLACK)
        name_rect = name_text.get_rect(centerx=card_rect.centerx, top=card_y + 50)
        self.screen.blit(name_text, name_rect)

        y_offset = name_rect.bottom + 20
        padding = 20

        price_text = self.font.render(
            f"Price: £{property_data['price']}", True, ACCENT_COLOR
        )
        self.screen.blit(price_text, (card_x + padding, y_offset))
        y_offset += 35

        rent_text = self.small_font.render(
            f"Base Rent: £{property_data.get('rent', 0)}", True, BLACK
        )
        self.screen.blit(rent_text, (card_x + padding, y_offset))
        y_offset += 25

        if "house_costs" in property_data:
            for i, cost in enumerate(property_data["house_costs"], 1):
                house_text = self.small_font.render(
                    f"{i} House{'s' if i > 1 else ''}: £{cost}", True, BLACK
                )
                self.screen.blit(house_text, (card_x + padding, y_offset))
                y_offset += 25

        if "Station" in property_data["name"]:
            rent_rules = [
                "1 Station: £25",
                "2 Stations: £50",
                "3 Stations: £100",
                "4 Stations: £200",
            ]
            for rule in rent_rules:
                rule_text = self.small_font.render(rule, True, BLACK)
                self.screen.blit(rule_text, (card_x + padding, y_offset))
                y_offset += 25
        elif property_data["name"] in ["Tesla Power Co", "Edison Water"]:
            utility_text = self.small_font.render(
                "Rent = 4x dice if 1 owned", True, BLACK
            )
            self.screen.blit(utility_text, (card_x + padding, y_offset))
            y_offset += 25
            utility_text2 = self.small_font.render(
                "Rent = 10x dice if both owned", True, BLACK
            )
            self.screen.blit(utility_text2, (card_x + padding, y_offset))

    def draw_buy_options(self, mouse_pos):
        if self.game.current_player_is_ai:
            window_size = self.screen.get_size()
            message = "AI player is deciding..."

            message_surface = self.font.render(message, True, GOLD)

            msg_x = (window_size[0] - message_surface.get_width()) // 2
            msg_y = window_size[1] // 4

            padding = 15
            bg_rect = pygame.Rect(
                msg_x - padding,
                msg_y - padding,
                message_surface.get_width() + (padding * 2),
                message_surface.get_height() + (padding * 2),
            )

            bg_surface = pygame.Surface(
                (bg_rect.width, bg_rect.height), pygame.SRCALPHA
            )
            bg_surface.fill((0, 0, 0, 180))
            self.screen.blit(bg_surface, (bg_rect.x, bg_rect.y))

            pygame.draw.rect(self.screen, ACCENT_COLOR, bg_rect, 2, border_radius=5)

            self.screen.blit(message_surface, (msg_x, msg_y))
            return

        window_size = self.screen.get_size()
        button_width = 100
        button_height = 40
        spacing = 20

        card_width = int(window_size[0] * 0.35)
        card_x = (window_size[0] - card_width) // 2
        card_y = (window_size[1] - card_width) // 2

        total_width = (button_width * 2) + spacing
        start_x = card_x + (card_width - total_width) // 2
        button_y = card_y + card_width - button_height - 20

        self.game.yes_button = pygame.Rect(
            start_x, button_y, button_width, button_height
        )
        self.game.no_button = pygame.Rect(
            start_x + button_width + spacing, button_y, button_width, button_height
        )

        yes_hover = self.game.yes_button.collidepoint(mouse_pos)
        no_hover = self.game.no_button.collidepoint(mouse_pos)

        self.draw_button(self.game.yes_button, "Buy", hover=yes_hover, active=True)
        self.draw_button(self.game.no_button, "Pass", hover=no_hover, active=True)

    def draw_property_tooltip(self, property_data, mouse_pos):
        padding = 10
        window_size = self.screen.get_size()

        tooltip_width = 250
        line_height = 25
        num_lines = 5
        if property_data.get("group"):
            num_lines += 1
        tooltip_height = num_lines * line_height + padding * 2

        x = min(mouse_pos[0] + 20, window_size[0] - tooltip_width - padding)
        y = min(mouse_pos[1] + 20, window_size[1] - tooltip_height - padding)

        shadow_surface = pygame.Surface(
            (tooltip_width + 4, tooltip_height + 4), pygame.SRCALPHA
        )
        pygame.draw.rect(
            shadow_surface, (0, 0, 0, 128), shadow_surface.get_rect(), border_radius=10
        )
        self.screen.blit(shadow_surface, (x + 2, y + 2))

        tooltip_surface = pygame.Surface(
            (tooltip_width, tooltip_height), pygame.SRCALPHA
        )
        pygame.draw.rect(
            tooltip_surface,
            (30, 30, 30, 240),
            tooltip_surface.get_rect(),
            border_radius=10,
        )

        if property_data.get("group"):
            header_height = 30
            header_color = GROUP_COLORS.get(property_data["group"], GRAY)
            pygame.draw.rect(
                tooltip_surface,
                header_color,
                (0, 0, tooltip_width, header_height),
                border_radius=10,
            )
            pygame.draw.rect(
                tooltip_surface,
                header_color,
                (0, header_height - 15, tooltip_width, 15),
            )

        self.screen.blit(tooltip_surface, (x, y))

        current_y = y + padding

        name_text = self.small_font.render(property_data["name"], True, WHITE)
        self.screen.blit(name_text, (x + padding, current_y))
        current_y += line_height

        if property_data.get("group"):
            group_text = self.small_font.render(
                f"Group: {property_data['group']}", True, LIGHT_GRAY
            )
            self.screen.blit(group_text, (x + padding, current_y))
            current_y += line_height

        price_text = self.small_font.render(
            f"Price: £{property_data.get('price', 0):,}", True, SUCCESS_COLOR
        )
        self.screen.blit(price_text, (x + padding, current_y))
        current_y += line_height

        base_rent = property_data.get("rent", 0)
        rent_text = self.small_font.render(
            f"Base Rent: £{base_rent:,}", True, ACCENT_COLOR
        )
        self.screen.blit(rent_text, (x + padding, current_y))
        current_y += line_height

        if property_data.get("houses", 0) > 0:
            houses = property_data["houses"]
            if houses == 5:
                hotel_text = self.small_font.render("Has Hotel", True, RED)
                self.screen.blit(hotel_text, (x + padding, current_y))
            else:
                house_text = self.small_font.render(
                    f"Houses Built: {houses}", True, GREEN
                )
                self.screen.blit(house_text, (x + padding, current_y))
            current_y += line_height
        elif property_data.get("has_hotel", False):
            hotel_text = self.small_font.render("Has Hotel", True, RED)
            self.screen.blit(hotel_text, (x + padding, current_y))
            current_y += line_height

        if property_data.get("mortgaged", False):
            mortgage_text = self.small_font.render("[MORTGAGED]", True, ERROR_COLOR)
            self.screen.blit(mortgage_text, (x + padding, current_y))
        else:
            mortgage_value = property_data.get("price", 0) // 2
            mortgage_text = self.small_font.render(
                f"Mortgage Value: £{mortgage_value:,}", True, LIGHT_GRAY
            )
            self.screen.blit(mortgage_text, (x + padding, current_y))

        pygame.draw.rect(
            self.screen,
            ACCENT_COLOR,
            (x, y, tooltip_width, tooltip_height),
            1,
            border_radius=10,
        )

    def draw_notification(self):
        if not self.game.notification:
            return

        current_time = pygame.time.get_ticks()
        if current_time - self.game.notification_time > self.game.NOTIFICATION_DURATION:
            self.game.notification = None
            return

        window_size = self.screen.get_size()
        padding = 20

        notification_text = self.font.render(self.game.notification, True, WHITE)
        bg_width = notification_text.get_width() + padding * 2
        bg_height = notification_text.get_height() + padding * 2
        bg_surface = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
        pygame.draw.rect(
            bg_surface,
            (*ACCENT_COLOR[:3], 230),
            bg_surface.get_rect(),
            border_radius=10,
        )

        for i in range(3):
            alpha = 100 - i * 30
            pygame.draw.rect(
                bg_surface,
                (*ACCENT_COLOR[:3], alpha),
                (-i, -i, bg_width + i * 2, bg_height + i * 2),
                border_radius=10,
            )

        x = (window_size[0] - bg_width) // 2
        y = 20

        self.screen.blit(bg_surface, (x, y))
        self.screen.blit(notification_text, (x + padding, y + padding))

    def draw_card_alert(self, card, player):
        window_size = self.screen.get_size()
        card_width = int(window_size[0] * 0.4)
        card_height = int(window_size[1] * 0.3)
        card_x = (window_size[0] - card_width) // 2
        card_y = (window_size[1] - card_height) // 2

        overlay = pygame.Surface(window_size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        shadow_rect = pygame.Rect(card_x + 6, card_y + 6, card_width, card_height)
        shadow = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (*BLACK, 128), shadow.get_rect(), border_radius=15)
        self.screen.blit(shadow, shadow_rect)

        card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
        pygame.draw.rect(self.screen, WHITE, card_rect, border_radius=15)

        header_height = 60
        header_rect = pygame.Rect(card_x, card_y, card_width, header_height)
        pygame.draw.rect(self.screen, ACCENT_COLOR, header_rect, border_radius=15)
        pygame.draw.rect(
            self.screen,
            ACCENT_COLOR,
            pygame.Rect(card_x, card_y + header_height - 15, card_width, 15),
        )

        header_text = self.font.render(card["type"], True, WHITE)
        header_shadow = self.font.render(card["type"], True, BLACK)
        header_rect = header_text.get_rect(
            center=(card_x + card_width // 2, card_y + header_height // 2)
        )
        shadow_rect = header_rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        self.screen.blit(header_shadow, shadow_rect)
        self.screen.blit(header_text, header_rect)

        player_y = card_y + header_height + 20
        player_text = self.font.render(f"Player: {player['name']}", True, BLACK)
        self.screen.blit(player_text, (card_x + 20, player_y))

        message_y = player_y + 40
        message_lines = self.wrap_text(card["message"], card_width - 40)
        for i, line in enumerate(message_lines):
            message_text = self.small_font.render(line, True, BLACK)
            self.screen.blit(message_text, (card_x + 20, message_y + i * 30))

        continue_y = card_y + card_height - 25
        continue_text = self.small_font.render(
            "Tap or click to continue...", True, GRAY
        )
        continue_rect = continue_text.get_rect(
            centerx=card_x + card_width // 2, bottom=continue_y
        )
        self.screen.blit(continue_text, continue_rect)

    def wrap_text(self, text, max_width):
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = " ".join(current_line + [word])
            test_surface = self.small_font.render(test_line, True, BLACK)
            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
                    current_line = []

        if current_line:
            lines.append(" ".join(current_line))

        return lines

    def draw_popup_message(self):
        window_size = self.screen.get_size()

        overlay = pygame.Surface(window_size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))

        popup_width = int(window_size[0] * 0.4)
        popup_height = int(window_size[1] * 0.25)
        popup_x = (window_size[0] - popup_width) // 2
        popup_y = (window_size[1] - popup_height) // 2

        shadow_offset = 4
        shadow = pygame.Surface((popup_width, popup_height))
        shadow.fill(BLACK)
        self.screen.blit(shadow, (popup_x + shadow_offset, popup_y + shadow_offset))

        pygame.draw.rect(
            self.screen, WHITE, (popup_x, popup_y, popup_width, popup_height)
        )
        pygame.draw.rect(
            self.screen, ACCENT_COLOR, (popup_x, popup_y, popup_width, popup_height), 2
        )

        if self.game.popup_title:
            title_surface = self.font.render(self.game.popup_title, True, ACCENT_COLOR)
            title_rect = title_surface.get_rect(
                centerx=popup_x + popup_width // 2, top=popup_y + 20
            )
            self.screen.blit(title_surface, title_rect)

        if self.game.popup_message:
            words = self.game.popup_message.split()
            lines = []
            current_line = []

            for word in words:
                test_line = " ".join(current_line + [word])
                test_surface = self.small_font.render(test_line, True, BLACK)
                if test_surface.get_width() <= popup_width - 40:
                    current_line.append(word)
                else:
                    lines.append(" ".join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(" ".join(current_line))

            y_offset = popup_y + 80
            for line in lines:
                text_surface = self.small_font.render(line, True, BLACK)
                text_rect = text_surface.get_rect(
                    centerx=popup_x + popup_width // 2, top=y_offset
                )
                self.screen.blit(text_surface, text_rect)
                y_offset += 30

        button_width = 100
        button_height = 40
        button_x = popup_x + (popup_width - button_width) // 2
        button_y = popup_y + popup_height - 60

        mouse_pos = pygame.mouse.get_pos()
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        button_color = (
            BUTTON_HOVER if button_rect.collidepoint(mouse_pos) else ACCENT_COLOR
        )

        pygame.draw.rect(self.screen, button_color, button_rect, border_radius=5)
        button_text = self.small_font.render("OK", True, WHITE)
        text_rect = button_text.get_rect(center=button_rect.center)
        self.screen.blit(button_text, text_rect)

    def draw_auction(self, auction_data):
        if self.game.show_card:
            print("Card is showing - not drawing auction UI")
            return

        if auction_data is None:
            print("Warning: Auction data is None in draw_auction")
            self.game.state = "ROLL"
            return

        required_keys = [
            "property",
            "current_bid",
            "minimum_bid",
            "highest_bidder",
            "current_bidder_index",
            "active_players",
        ]

        for key in required_keys:
            if key not in auction_data:
                print(
                    f"Warning: Auction data missing key '{key}' - resetting to ROLL state"
                )
                self.game.state = "ROLL"
                return

        if (
            not isinstance(auction_data["property"], dict)
            or "name" not in auction_data["property"]
        ):
            print("Warning: Auction property data is invalid - resetting to ROLL state")
            self.game.state = "ROLL"
            return

        current_bidder_index = auction_data.get("current_bidder_index", 0)
        if current_bidder_index < len(auction_data["active_players"]):
            current_bidder = auction_data["active_players"][current_bidder_index]
            if current_bidder.get("is_ai", False):
                ai_player = current_bidder
                print(f"Auto-handling AI auction turn for {ai_player['name']}")
                self.game.handle_ai_turn(ai_player)
                pygame.time.delay(500)

        print(f"\n=== Drawing Auction UI ===")
        print(f"Property: {auction_data['property']['name']}")
        print(f"Current bid: £{auction_data['current_bid']}")
        print(f"Minimum bid: £{auction_data['minimum_bid']}")

        if auction_data["highest_bidder"]:
            print(f"Highest bidder: {auction_data['highest_bidder']['name']}")
        else:
            print("No bids yet")

        print(f"Current bidder index: {auction_data['current_bidder_index']}")
        if auction_data["active_players"]:
            current_bidder = auction_data["active_players"][
                auction_data["current_bidder_index"]
            ]
            print(f"Current bidder: {current_bidder['name']}")

        print(f"Passed players: {auction_data.get('passed_players', set())}")
        print(
            f"Active players: {[p['name'] for p in auction_data.get('active_players', [])]}"
        )
        print(f"Completed: {auction_data.get('completed', False)}")

        window_size = self.screen.get_size()
        card_width = int(window_size[0] * 0.35)
        card_height = int(window_size[1] * 0.5)
        card_x = (window_size[0] - card_width) // 2
        card_y = (window_size[1] - card_height) // 2

        overlay = pygame.Surface(window_size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        for i in range(5):
            shadow_offset = 6 - i
            shadow_rect = pygame.Rect(
                card_x + shadow_offset, card_y + shadow_offset, card_width, card_height
            )
            shadow = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
            shadow_alpha = 100 - (i * 20)
            pygame.draw.rect(
                shadow, (*BLACK, shadow_alpha), shadow.get_rect(), border_radius=15
            )
            self.screen.blit(shadow, shadow_rect)

        pygame.draw.rect(
            self.screen,
            WHITE,
            (card_x, card_y, card_width, card_height),
            border_radius=15,
        )

        current_time = pygame.time.get_ticks()
        time_remaining = max(
            0,
            (auction_data["start_time"] + auction_data["duration"] - current_time)
            // 1000,
        )

        current_bidder = auction_data["active_players"][
            auction_data["current_bidder_index"]
        ]
        current_bidder_obj = next(
            (p for p in self.game.players if p.name == current_bidder["name"]), None
        )

        header_color = ERROR_COLOR if time_remaining <= 10 else ACCENT_COLOR
        header_text = self.font.render(
            f"{current_bidder['name']}'s Turn", True, header_color
        )
        timer_text = self.font.render(f"Time: {time_remaining}s", True, header_color)

        header_y = card_y + 20
        self.screen.blit(header_text, (card_x + 20, header_y))
        self.screen.blit(
            timer_text, (card_x + card_width - timer_text.get_width() - 20, header_y)
        )

        title_y = header_y + 50
        title = self.font.render("AUCTION", True, BLACK)
        property_name = self.font.render(auction_data["property"]["name"], True, BLACK)
        self.screen.blit(
            title, (card_x + (card_width - title.get_width()) // 2, title_y)
        )
        self.screen.blit(property_name, (card_x + 20, title_y + 40))

        info_y = title_y + 90
        current_bid = self.font.render(
            f"Current Bid: £{auction_data['current_bid']}", True, BLACK
        )
        min_bid = self.font.render(
            f"Minimum Bid: £{auction_data['minimum_bid']}", True, BLACK
        )
        self.screen.blit(current_bid, (card_x + 20, info_y))
        self.screen.blit(min_bid, (card_x + 20, info_y + 40))

        if auction_data["highest_bidder"]:
            highest_y = info_y + 80
            highest_text = self.font.render(
                f"Highest Bidder: {auction_data['highest_bidder']['name']}",
                True,
                SUCCESS_COLOR,
            )
            self.screen.blit(highest_text, (card_x + 20, highest_y))

        can_bid = current_bidder["name"] not in auction_data.get(
            "passed_players", set()
        )
        is_human = current_bidder_obj and not current_bidder_obj.is_ai

        if is_human and can_bid:
            self.game.auction_input = pygame.Rect(
                card_x + 20, card_y + card_height - 120, 200, 40
            )
            pygame.draw.rect(self.screen, WHITE, self.game.auction_input)
            pygame.draw.rect(self.screen, ACCENT_COLOR, self.game.auction_input, 2)

            if self.game.auction_bid_amount:
                bid_text = self.font.render(self.game.auction_bid_amount, True, BLACK)
            else:
                bid_text = self.small_font.render("Enter bid amount...", True, GRAY)
            self.screen.blit(
                bid_text,
                (
                    self.game.auction_input.x + 10,
                    self.game.auction_input.y
                    + (self.game.auction_input.height - bid_text.get_height()) // 2,
                ),
            )

            button_width = 100
            button_height = 40
            button_margin = 20

            self.game.auction_buttons = {
                "bid": pygame.Rect(
                    card_x + 20, card_y + card_height - 60, button_width, button_height
                ),
                "pass": pygame.Rect(
                    card_x + 20 + button_width + button_margin,
                    card_y + card_height - 60,
                    button_width,
                    button_height,
                ),
            }

            mouse_pos = pygame.mouse.get_pos()
            for btn_name, btn_rect in self.game.auction_buttons.items():
                mouse_over = btn_rect.collidepoint(mouse_pos)
                color = BUTTON_HOVER if mouse_over else ACCENT_COLOR
                pygame.draw.rect(self.screen, color, btn_rect, border_radius=5)

                btn_text = self.font.render(btn_name.title(), True, WHITE)
                self.screen.blit(
                    btn_text,
                    (
                        btn_rect.centerx - btn_text.get_width() // 2,
                        btn_rect.centery - btn_text.get_height() // 2,
                    ),
                )

        if auction_data.get("passed_players"):
            passed_text = self.small_font.render(
                "Passed: " + ", ".join(auction_data["passed_players"]), True, GRAY
            )
            self.screen.blit(passed_text, (card_x + 20, card_y + card_height - 30))

    def draw_jail_options(self, player):
        if not player.get("in_jail", False):
            return

        window_size = self.screen.get_size()
        card_width = int(window_size[0] * 0.3)
        card_height = int(window_size[1] * 0.3)
        card_x = (window_size[0] - card_width) // 2
        card_y = (window_size[1] - card_height) // 2

        overlay = pygame.Surface(window_size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.screen.blit(overlay, (0, 0))

        shadow_rect = pygame.Rect(card_x + 6, card_y + 6, card_width, card_height)
        shadow = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (*BLACK, 128), shadow.get_rect(), border_radius=15)
        self.screen.blit(shadow, shadow_rect)

        pygame.draw.rect(
            self.screen,
            WHITE,
            (card_x, card_y, card_width, card_height),
            border_radius=15,
        )

        title_text = self.font.render("Jail Options", True, ACCENT_COLOR)
        title_rect = title_text.get_rect(
            centerx=card_x + card_width // 2, y=card_y + 20
        )
        self.screen.blit(title_text, title_rect)

        options = []
        if player.get("jail_card", False):
            options.append(("Use Get Out of Jail Free Card", "card"))
        if player.get("money", 0) >= 50:
            options.append(("Pay £50 Fine", "pay"))
        options.append(("Roll for Doubles", "roll"))

        button_height = 40
        button_margin = 10
        y_offset = card_y + 80
        mouse_pos = pygame.mouse.get_pos()

        for i, (option_text, key) in enumerate(options):
            button_rect = pygame.Rect(
                card_x + 20, y_offset, card_width - 40, button_height
            )
            is_hovered = button_rect.collidepoint(mouse_pos)

            self.draw_button(button_rect, option_text, hover=is_hovered, active=True)

            y_offset += button_height + button_margin

        turns_text = self.small_font.render(
            f"Turns in jail: {player.get('jail_turns', 0)}/3", True, ERROR_COLOR
        )
        turns_rect = turns_text.get_rect(
            centerx=card_x + card_width // 2, bottom=card_y + card_height - 20
        )
        self.screen.blit(turns_text, turns_rect)

    def draw_free_parking_pot(self):
        window_size = self.screen.get_size()

        panel_width = 200
        panel_height = 100
        panel_x = 10
        panel_y = 230

        glow_surface = pygame.Surface(
            (panel_width + 10, panel_height + 10), pygame.SRCALPHA
        )
        for i in range(5):
            alpha = int(100 * (1 - i / 5))
            pygame.draw.rect(
                glow_surface,
                (*ACCENT_COLOR[:3], alpha),
                pygame.Rect(i, i, panel_width + 10 - i * 2, panel_height + 10 - i * 2),
                border_radius=10,
            )
        self.screen.blit(glow_surface, (panel_x - 5, panel_y - 5))

        panel = pygame.Surface((panel_width, panel_height))
        panel.fill(UI_BG)
        self.screen.blit(panel, (panel_x, panel_y))

        title_text = self.small_font.render("Free Parking Pot", True, LIGHT_GRAY)
        title_rect = title_text.get_rect(
            centerx=panel_x + panel_width // 2, top=panel_y + 10
        )
        self.screen.blit(title_text, title_rect)

        money_color = SUCCESS_COLOR if self.game.free_parking_pot > 0 else LIGHT_GRAY
        money_text = self.font.render(
            f"£{self.game.free_parking_pot:,}", True, money_color
        )
        money_rect = money_text.get_rect(
            centerx=panel_x + panel_width // 2, top=title_rect.bottom + 10
        )
        self.screen.blit(money_text, money_rect)

    def handle_development_click(self, pos, property_data):

        return self.game.dev_manager.handle_click(pos)
