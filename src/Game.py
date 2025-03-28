# Property Tycoon Game.py
# It contains the classes for managing the game state, rules, and player interactions

import pygame
import sys
import os
import time
import random
import math
from src.Board import Board
from src.Property import Property
from src.Game_Logic import GameLogic
from src.Cards import CardType, CardDeck
from src.Font_Manager import font_manager
from src.Ai_Player_Logic import EasyAIPlayer, HardAIPlayer
from typing import Optional
import string
from src.UI import DevelopmentNotification, AIEmotionUI
from src.GameRenderer import GameRenderer
from src.GameEventHandler import GameEventHandler
from src.GameActions import GameActions
from src.DevelopmentMode import DevelopmentMode

base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATH = os.path.join(base_path, "assets", "font", "Ticketing.ttf")

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

KEY_ROLL = [pygame.K_SPACE, pygame.K_RETURN]
KEY_BUY = [pygame.K_y, pygame.K_RETURN]
KEY_PASS = [pygame.K_n, pygame.K_ESCAPE]


class Game:
    def __init__(
        self, players, game_mode="full", time_limit=None, ai_difficulty="easy"
    ):
        if not pygame.get_init():
            pygame.init()

        info = pygame.display.Info()
        self.screen = pygame.display.get_surface()
        if not self.screen:
            self.screen = pygame.display.set_mode((info.current_w, info.current_h))
        pygame.display.set_caption("Property Tycoon Alpha 25.03.2025")

        self.renderer = None
        self.game_actions = GameActions(self)
        self.development_mode = False

        self.font = font_manager.get_font(32)
        self.small_font = font_manager.get_font(24)
        self.tiny_font = font_manager.get_font(16)
        self.button_font = font_manager.get_font(32)
        self.message_font = font_manager.get_font(24)

        self.dev_manager = DevelopmentMode(self, self.game_actions)

        window_size = self.screen.get_size()
        try:
            bg_path = os.path.join(base_path, "assets/image/starterbackground.png")
            self.original_background = pygame.image.load(bg_path)
            background = pygame.transform.scale(self.original_background, window_size)

            board_path = os.path.join(base_path, "assets/image/board.png")
            self.original_board = pygame.image.load(board_path)

            board_width = int(window_size[0] * 0.3)
            board_height = int(board_width)
            board_image = pygame.transform.scale(
                self.original_board, (board_width, board_height)
            )

            board_x = (window_size[0] - board_width) // 2
            board_y = (window_size[1] - board_height) // 2 - 50

            self.screen.blit(background, (0, 0))

            overlay = pygame.Surface(window_size, pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            border_size = 10
            border_rect = pygame.Rect(
                board_x - border_size,
                board_y - border_size,
                board_width + (border_size * 2),
                board_height + (border_size * 2),
            )
            pygame.draw.rect(self.screen, (218, 165, 32), border_rect, border_radius=10)

            for alpha in range(0, 256, 10):
                board_surface = board_image.copy()
                board_surface.set_alpha(alpha)
                self.screen.blit(background, (0, 0))
                self.screen.blit(overlay, (0, 0))
                pygame.draw.rect(
                    self.screen, (218, 165, 32), border_rect, border_radius=10
                )
                self.screen.blit(board_surface, (board_x, board_y))

                tip_text = "TIP: You can move the board position using WASD and zoom with +/- keys"

                shadow_surface = self.small_font.render(tip_text, True, (0, 0, 0))
                shadow_rect = shadow_surface.get_rect(
                    center=(window_size[0] // 2 + 2, window_size[1] - 100 + 2)
                )
                shadow_surface.set_alpha(min(alpha, 150))
                self.screen.blit(shadow_surface, shadow_rect)

                text_surface = self.small_font.render(tip_text, True, (255, 255, 255))
                text_rect = text_surface.get_rect(
                    center=(window_size[0] // 2, window_size[1] - 100)
                )
                text_surface.set_alpha(alpha)
                self.screen.blit(text_surface, text_rect)

                pygame.display.flip()
                pygame.time.delay(20)

            pygame.time.wait(2000)

            shuffling_path = os.path.join(base_path, "assets/image/Cards shuffling.png")
            self.original_shuffling = pygame.image.load(shuffling_path)
            shuffling_image = pygame.transform.scale(
                self.original_shuffling, window_size
            )

            self.screen.blit(background, (0, 0))
            self.screen.blit(shuffling_image, (0, 0))
            pygame.display.flip()
            pygame.time.wait(1000)

            start_path = os.path.join(base_path, "assets/image/Gamestart.png")
            self.original_start_image = pygame.image.load(start_path)
            logo_width = int(window_size[0] * 0.5)
            logo_height = int(
                logo_width
                * (
                    self.original_start_image.get_height()
                    / self.original_start_image.get_width()
                )
            )
            start_image = pygame.transform.scale(
                self.original_start_image, (logo_width, logo_height)
            )

            self.screen.blit(background, (0, 0))
            overlay = pygame.Surface(window_size, pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            self.screen.blit(overlay, (0, 0))
            logo_x = (window_size[0] - logo_width) // 2
            logo_y = (window_size[1] - logo_height) // 2
            self.screen.blit(start_image, (logo_x, logo_y))
            pygame.display.flip()
            pygame.time.wait(1000)
        except Exception as e:
            print(f"Error loading startup animations: {e}")

        self.game_mode = game_mode
        self.time_limit = time_limit
        self.ai_difficulty = ai_difficulty
        self.start_time = pygame.time.get_ticks() if time_limit else None

        if self.game_mode == "abridged" and self.time_limit:
            minutes = self.time_limit // 60
            print(
                f"Game initialized in Abridged mode with {minutes} minutes time limit"
            )
            print(f"Time limit in seconds: {self.time_limit}")
        else:
            print(f"Game initialized in Full mode (no time limit)")

        self.rounds_completed = {player.name: 0 for player in players}
        self.lap_count = {player.name: 0 for player in players}

        self.game_over = False
        self.winner_index = None
        self.time_limit_reached = False
        self.final_lap = {}

        self.time_warning_start = 60
        self.warning_flash_rate = 500

        self.auction_completed = False
        self.auction_end_time = 0
        self.auction_end_delay = 3000

        self.dice_images = {}
        try:
            for i in range(1, 7):
                dice_path = os.path.join(
                    base_path, "assets", "image", "Dice", f"{i}.png"
                )
                if os.path.exists(dice_path):
                    print(f"Loading dice image: {dice_path}")
                    self.dice_images[i] = pygame.image.load(dice_path)
                else:
                    print(f"Dice image not found: {dice_path}")
        except Exception as e:
            print(f"Error loading dice images: {e}")

        try:
            self.logic = GameLogic()
            self.logic.game = self
            self.logic.ai_difficulty = self.ai_difficulty

            if self.ai_difficulty == "hard":
                from src.Ai_Player_Logic import HardAIPlayer

                self.logic.ai_player = HardAIPlayer()
            else:
                from src.Ai_Player_Logic import EasyAIPlayer

                self.logic.ai_player = EasyAIPlayer()

            if not self.logic.game_start():
                raise RuntimeError("Failed to initialize game data")

            if not players:
                raise ValueError("No players provided")

            self.players = players
            self.board = Board(self.players)

            from src.Cards import CardDeck, CardType

            self.pot_luck_deck = CardDeck(CardType.POT_LUCK)
            self.opportunity_deck = CardDeck(CardType.OPPORTUNITY_KNOCKS)

            self.board.update_board_positions()
            self.board.update_ownership(self.logic.properties)

            self.state = "ROLL"
            self.current_property = None
            self.last_roll = None
            self.roll_time = 0
            self.ROLL_DISPLAY_TIME = 2000

            self.animation_start = 0
            self.animation_duration = 1000
            self.dice_animation = False
            self.dice_values = None

            self.player_colors = {}

            for i, player in enumerate(players):
                if not self.logic.add_player(player.name):
                    raise RuntimeError(f"Failed to add player {player.name}")
                self.player_colors[player.name] = player.color

            window_size = self.screen.get_size()
            button_width = 120
            button_height = 45
            button_margin = 20
            button_y = window_size[1] - button_height - button_margin

            self.roll_button = pygame.Rect(
                window_size[0] - button_width - button_margin,
                button_y,
                button_width,
                button_height,
            )

            self.quit_button = pygame.Rect(
                window_size[0] - (button_width * 2) - (button_margin * 2),
                button_y,
                button_width,
                button_height,
            )

            self.pause_button = pygame.Rect(
                window_size[0] - (button_width * 2) - (button_margin * 2),
                button_y - button_height - button_margin,
                button_width,
                button_height,
            )

            self.game_paused = False
            self.pause_start_time = 0
            self.total_pause_time = 0

            self.yes_button = pygame.Rect(
                window_size[0] - (button_width * 2) - (button_margin * 2),
                button_y,
                button_width,
                button_height,
            )

            self.no_button = pygame.Rect(
                window_size[0] - button_width - button_margin,
                button_y,
                button_width,
                button_height,
            )

            self.auction_buttons = {
                "bid": pygame.Rect(0, 0, 120, 40),
                "pass": pygame.Rect(0, 0, 120, 40),
            }
            self.auction_input = pygame.Rect(0, 0, 200, 40)
            self.auction_bid_amount = ""

            self.current_player_is_ai = False
            self.notification = None
            self.notification_time = 0
            self.NOTIFICATION_DURATION = 3000

            self.show_popup = False
            self.popup_message = None
            self.popup_title = None

            self.show_card = False
            self.current_card = None
            self.current_card_player = None
            self.card_display_time = 0
            self.CARD_DISPLAY_DURATION = 3000

            self.free_parking_pot = 0

            self.emotion_uis = {}
            for player in self.players:
                if player.is_ai and self.ai_difficulty == "hard":
                    self.emotion_uis[player.name] = AIEmotionUI(
                        self.screen, player, self
                    )
                    print(f"Initialized emotion UI for {player.name}")

        except Exception as e:
            print(f"Error during game initialization: {e}")
            pygame.quit()
            raise

        self.update_current_player()

    def add_message(self, text):
        self.board.add_message(text)

    def finish_dice_animation(self):
        if not self.dice_animation or not self.dice_values:
            return

        print("\n=== Dice Roll Debug ===")
        self.dice_animation = False
        dice1, dice2 = self.dice_values
        print(f"Dice roll: {dice1, dice2} (Total: {dice1 + dice2})")

        self.last_roll = (dice1, dice2)
        self.roll_time = pygame.time.get_ticks()
        current_player = self.logic.players[self.logic.current_player_index]

        print(f"Current player: {current_player['name']}")
        print(f"Current position: {current_player['position']}")

        self.wait_for_animations()

        while self.logic.message_queue:
            message = self.logic.message_queue.pop(0)
            print(f"Processing message: {message}")
            self.board.add_message(message)

        if current_player.get("in_jail", False):
            print("Player is in jail")
            if dice1 == dice2:
                print("Rolled doubles - getting out of jail")
                current_player["in_jail"] = False
                current_player["jail_turns"] = 0
                self.board.add_message(
                    f"{current_player['name']} rolled doubles ({dice1},{dice2}) and left jail!"
                )

                for player in self.players:
                    if player.name == current_player["name"]:
                        player.in_jail = False
                        break
            else:
                print("Failed to roll doubles - staying in jail")
                self.game_actions.handle_jail_turn(current_player)
                self.state = "ROLL"
                self.renderer.draw()
                pygame.display.flip()
                return

        position = current_player["position"]
        print(f"Landing on position: {position}")

        self.board.update_board_positions()
        self.board.update_ownership(self.logic.properties)

        current_player_obj = next(
            (p for p in self.players if p.name == current_player["name"]), None
        )

        if position == 20:
            print(f"Player landed on Free Parking space")
            self.board.add_message(f"{current_player['name']} landed on Free Parking")

            self.game_actions.collect_free_parking(current_player)

            self.state = "ROLL"
            self.renderer.draw()
            pygame.display.flip()
            return

        card_type = None
        if position == 3 or position == 18 or position == 34:
            print(f"Player landed on Pot Luck space {position}")
            card_type = "POT_LUCK"
            self.board.add_message(f"{current_player['name']} landed on Pot Luck")

            result = self.handle_card_draw(current_player, card_type)
            if result == "moved":
                self.wait_for_animations()
                self.board.update_board_positions()
                self.renderer.draw()
                pygame.display.flip()

        elif position == 8 or position == 23 or position == 37:
            print(f"Player landed on Opportunity Knocks space {position}")
            card_type = "OPPORTUNITY_KNOCKS"
            self.board.add_message(
                f"{current_player['name']} landed on Opportunity Knocks"
            )

            result = self.handle_card_draw(current_player, card_type)
            if result == "moved":
                self.wait_for_animations()
                self.board.update_board_positions()
                self.renderer.draw()
                pygame.display.flip()

        if str(position) in self.logic.properties and not card_type:
            space = self.logic.properties[str(position)]
            print(f"\nLanded on property: {space['name']}")
            print(f"Property owner: {space.get('owner', 'None')}")

            if space["name"] == "Go to Jail":
                print("Go to Jail space - moving player to jail")
                self.board.add_message(f"{current_player['name']} goes to Jail!")
                current_player["in_jail"] = True
                current_player["jail_turns"] = 0
                current_player["position"] = 11

                for player in self.players:
                    if player.name == current_player["name"]:
                        player.position = 11
                        player.in_jail = True
                        player.jail_turns = 0
                        player.just_went_to_jail = True
                        break

                self.logic.is_going_to_jail = True
                self.handle_turn_end()
                self.state = "ROLL"
                self.board.update_board_positions()
                self.renderer.draw()
                pygame.display.flip()
            elif (
                "price" in space
                and space.get("owner") is None
                and not current_player.get("in_jail", False)
            ):
                if current_player.get("in_jail", False):
                    print("Player in jail - cannot buy property")
                    self.board.add_message(
                        f"{current_player['name']} cannot buy property while in jail!"
                    )
                    self.state = "ROLL"
                    self.renderer.draw()
                    pygame.display.flip()
                else:
                    print("\nUnowned property - initiating buy sequence")
                    print(f"Property price: £{space['price']}")
                    print(f"Player money: £{current_player['money']}")

                    if self.logic.completed_circuits.get(current_player["name"], 0) < 1:
                        message = f"{current_player['name']} must pass GO before buying property"
                        self.board.add_message(message)
                        print(
                            "Player has not completed a circuit - cannot buy property"
                        )
                        self.state = "ROLL"
                        self.renderer.draw()
                        pygame.display.flip()
                        return False

                    self.board.add_message(
                        f"{current_player['name']} landed on {space['name']}"
                    )
                    self.board.add_message(
                        f"Buy {space['name']} for £{space['price']}?"
                    )

                    self.state = "BUY"
                    self.current_property = space
                    print("Buy state activated")

                    self.renderer.draw()
                    pygame.display.flip()
                    pygame.time.delay(500)

                    if current_player_obj and current_player_obj.is_ai:
                        print("\nAI player making purchase decision")
                        pygame.time.delay(1000)
                        will_buy = (
                            random.random() < 0.7
                            and current_player["money"] >= space["price"]
                        )
                        print(f"AI decision: {'Buy' if will_buy else 'Pass'}")
                        self.game_actions.handle_buy_decision(will_buy)
            else:
                print("Property already owned or not purchasable")
                self.state = "ROLL"
                self.renderer.draw()
                pygame.display.flip()

                if current_player_obj and current_player_obj.is_ai:
                    property_to_develop = (
                        self.logic.ai_player.handle_property_development(
                            current_player, self.logic.properties
                        )
                    )
                    if property_to_develop:
                        house_cost = property_to_develop["price"] / 2
                        if current_player["money"] >= house_cost:
                            property_to_develop["houses"] = (
                                property_to_develop.get("houses", 0) + 1
                            )
                            current_player["money"] -= house_cost
                            self.board.add_message(
                                f"{current_player['name']} built a house on {property_to_develop['name']}"
                            )
                            self.board.update_ownership(self.logic.properties)
        else:
            print("Not a property space or already processed by card handling")
            self.state = "ROLL"
            self.renderer.draw()
            pygame.display.flip()

        if self.state != "BUY":
            self.update_current_player()

        self.wait_for_animations()

        while self.logic.message_queue:
            message = self.logic.message_queue.pop(0)
            print(f"Processing message: {message}")
            self.board.add_message(message)
            if "Get Out of Jail Free card" in message or "collected" in message:
                self.board.add_message(message)

        print(f"\nFinal state: {self.state}")
        print("=== End Dice Roll Debug ===\n")

        self.renderer.draw()
        pygame.display.flip()

        self.development_mode = True

        current_player = self.logic.players[self.logic.current_player_index]
        owned_properties = [
            p
            for p in self.logic.properties.values()
            if p.get("owner") == current_player["name"]
        ]

        if not owned_properties:
            self.development_mode = False

        self.logic.is_going_to_jail = False

        self.renderer.draw()
        pygame.display.flip()

    def check_game_over(self):
        current_time = pygame.time.get_ticks()
        end_game_data = None

        if self.game_mode == "full":
            if not self.logic.players:
                if self.logic.bankrupted_players:
                    winner = (
                        self.logic.bankrupted_players[-2]
                        if len(self.logic.bankrupted_players) > 1
                        else None
                    )
                    self.game_over = True
                    return {
                        "winner": winner,
                        "bankrupted_players": self.logic.bankrupted_players,
                        "voluntary_exits": self.logic.voluntary_exits,
                    }
                return None

            active_players = [p for p in self.logic.players if p["money"] > 0]
            if len(active_players) <= 1:
                winner = active_players[0]["name"] if active_players else None
                self.game_over = True
                return {
                    "winner": winner,
                    "bankrupted_players": self.logic.bankrupted_players,
                    "voluntary_exits": self.logic.voluntary_exits,
                }

            human_players = [
                p
                for p in self.players
                if not p.is_ai and not p.bankrupt and not p.voluntary_exit
            ]
            ai_players = [
                p
                for p in self.players
                if p.is_ai and not p.bankrupt and not p.voluntary_exit
            ]

            if len(human_players) == 0 and len(ai_players) == 1:
                winner = ai_players[0].name
                self.game_over = True
                return {
                    "winner": winner,
                    "bankrupted_players": self.logic.bankrupted_players,
                    "voluntary_exits": self.logic.voluntary_exits,
                }

        elif self.game_mode == "abridged":
            if (
                self.time_limit
                and (current_time - self.start_time) // 1000 >= self.time_limit
            ):
                active_players = [
                    p["name"] for p in self.logic.players if not p.get("exited", False)
                ]

                if active_players:
                    min_laps = min([self.lap_count[p] for p in active_players])
                    if all(self.lap_count[p] == min_laps for p in active_players):
                        assets = {}
                        for player in self.logic.players:
                            total = player["money"]
                            for prop in self.logic.properties.values():
                                if prop.get("owner") == player["name"]:
                                    total += prop.get("price", 0)
                                    if "houses" in prop:
                                        house_costs = prop.get("house_costs", [])
                                        houses_count = prop["houses"]
                                        if house_costs and houses_count > 0:
                                            total += sum(house_costs[:houses_count])
                            assets[player["name"]] = total

                        max_asset_value = max(assets.values())

                        winners = [
                            player
                            for player, value in assets.items()
                            if value == max_asset_value
                        ]

                        if len(winners) == 1:
                            winner = winners[0]
                        else:
                            winner = "Tie"

                        self.game_over = True
                        return {
                            "winner": winner,
                            "tied_winners": winners if len(winners) > 1 else None,
                            "final_assets": assets,
                            "bankrupted_players": self.logic.bankrupted_players,
                            "voluntary_exits": self.logic.voluntary_exits,
                            "lap_count": self.lap_count,
                        }

        return None

    def handle_space(self, current_player):
        position = str(current_player["position"])
        if position not in self.logic.properties:
            return None, None

        space = self.logic.properties[position]

        if position == "20":
            print(f"Player landed on Free Parking space")
            self.board.add_message(f"{current_player['name']} landed on Free Parking")

            self.game_actions.collect_free_parking(current_player)
            return "free_parking", None

        if (
            "price" in space
            and space["owner"] is None
            and not current_player.get("in_jail", False)
        ):
            self.current_property = space
            self.state = "BUY"

            if self.logic.completed_circuits.get(current_player["name"], 0) < 1:
                self.game_actions.start_auction(space)
                self.renderer.draw()
                pygame.display.flip()
                return None, None

            player_obj = next(
                (p for p in self.players if p.name == current_player["name"]), None
            )
            is_ai_player = (
                player_obj.is_ai if player_obj else current_player.get("is_ai", False)
            )

            if not is_ai_player:
                self.board.add_message(
                    f"Would you like to buy {space['name']} for £{space['price']}?"
                )
                self.renderer.draw()
                pygame.display.flip()
                return "can_buy", None
            else:
                if self.logic.ai_player.should_buy_property(
                    space,
                    current_player["money"],
                    [
                        p
                        for p in self.logic.properties.values()
                        if p.get("owner") == current_player["name"]
                    ],
                ):
                    self.game_actions.handle_buy_decision(True)
                else:
                    self.game_actions.handle_buy_decision(False)
                return None, None

        result, message = self.logic.handle_space(current_player)

        if result == "free_parking":
            print(f"Game_Logic detected Free Parking space")
            self.board.add_message(f"{current_player['name']} landed on Free Parking")

            self.game_actions.collect_free_parking(current_player)
            return "free_parking", None

        return result, message

    def handle_game_over(self, winner_name):
        if self.game_over:
            return

        self.game_over = True
        if winner_name:
            for i, player in enumerate(self.players):
                if player.name == winner_name:
                    self.winner_index = i
                    player.set_winner(True)
                    self.board.add_message(f"*** {winner_name} wins! ***")
                    break

    def get_jail_choice(self, player):
        player_obj = next((p for p in self.players if p.name == player["name"]), None)
        if player_obj and player_obj.is_ai:
            if self.logic.jail_free_cards.get(player["name"], 0) > 0:
                return "card"
            elif player["money"] >= 50 and random.random() < 0.5:
                return "pay"
            return "roll"

        if self.game_mode == "abridged" and self.check_time_limit():
            print(
                "Time limit reached during jail choice - automatically returning 'roll'"
            )
            return "roll"

        if player["money"] < 50 and not self.logic.jail_free_cards.get(
            player["name"], 0
        ):
            self.board.add_message("No options available - must try rolling doubles")
            return "roll"

        waiting = True
        choice = None
        self.board.add_message("Choose how to get out of jail")

        window_size = self.screen.get_size()
        card_width = int(window_size[0] * 0.3)
        card_height = int(window_size[1] * 0.3)
        card_x = (window_size[0] - card_width) // 2
        card_y = (window_size[1] - card_height) // 2

        button_height = 40
        button_margin = 10
        title_height = 50
        y_start = card_y + title_height + 20

        options = []
        if self.logic.jail_free_cards.get(player["name"], 0) > 0:
            options.append(("[1] Use Get Out of Jail Free card", "card"))
        if player["money"] >= 50:
            options.append(("[2] Pay £50 fine", "pay"))
        options.append(("[3] Try rolling doubles", "roll"))
        options.append(("[4] Stay in jail (skip 2 turns)", "stay"))

        button_rects = []
        y_offset = y_start
        for option_text, option_value in options:
            button_rect = pygame.Rect(
                card_x + 20, y_offset, card_width - 40, button_height
            )
            button_rects.append((button_rect, option_value))
            y_offset += button_height + button_margin

        need_redraw = True
        last_redraw_time = 0
        last_click_time = 0

        while waiting:
            if self.game_mode == "abridged" and self.check_time_limit():
                print("Time limit reached during jail choice loop - breaking out")
                choice = "roll"
                break

            current_time = pygame.time.get_ticks()

            if current_time - last_redraw_time < 16:
                pygame.time.delay(5)
                continue

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if (
                        event.key == pygame.K_1
                        and self.logic.jail_free_cards.get(player["name"], 0) > 0
                    ):
                        choice = "card"
                        waiting = False
                    elif event.key == pygame.K_2 and player["money"] >= 50:
                        choice = "pay"
                        waiting = False
                    elif event.key == pygame.K_3:
                        choice = "roll"
                        waiting = False
                    elif event.key == pygame.K_4:
                        choice = "stay"
                        waiting = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if current_time - last_click_time < 300:
                        continue
                    last_click_time = current_time

                    mouse_pos = event.pos
                    for button_rect, option_value in button_rects:
                        if button_rect.collidepoint(mouse_pos):
                            if (
                                option_value == "card"
                                and self.logic.jail_free_cards.get(player["name"], 0)
                                > 0
                            ):
                                choice = "card"
                                waiting = False
                            elif option_value == "pay" and player["money"] >= 50:
                                choice = "pay"
                                waiting = False
                            elif option_value == "roll":
                                choice = "roll"
                                waiting = False
                            elif option_value == "stay":
                                choice = "stay"
                                waiting = False
                elif event.type == pygame.MOUSEMOTION:
                    need_redraw = True
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            if need_redraw:
                self.renderer.draw()
                if hasattr(self.renderer, "draw_jail_options"):
                    self.renderer.draw_jail_options(player)
                pygame.display.flip()
                need_redraw = False
                last_redraw_time = current_time

        return choice or "roll"

    def handle_card_action(self, card, player):
        print(f"Processing card action: {card.text} for player {player['name']}")

        self.show_card = True
        self.current_card = {"type": card.card_type.name, "message": card.text}
        self.current_card_player = player
        self.card_display_time = pygame.time.get_ticks()

        pygame.event.clear()
        waiting = True
        while waiting:
            self.renderer.draw()
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type in [pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN]:
                    waiting = False
                    self.show_card = False
                    self.current_card = None
                    self.current_card_player = None
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.time.wait(30)

        result = card.action(player, self)

        return result

    def show_card_popup(self, card_type, message):
        self.show_card = True
        self.current_card = {"type": card_type, "message": message}
        self.current_card_player = self.logic.players[self.logic.current_player_index]
        self.card_display_time = pygame.time.get_ticks()

        print(f"Showing card popup: {card_type} - {message}")

    def show_rent_popup(self, player, owner, property_name, rent_amount):
        self.show_card = True
        self.current_card = {
            "type": "Rent Payment",
            "message": f"You landed on {property_name} owned by {owner['name']}. Pay £{rent_amount} rent.",
        }
        self.current_card_player = player
        self.card_display_time = pygame.time.get_ticks()

        self.board.add_message(
            f"{player['name']} paid £{rent_amount} rent to {owner['name']} for {property_name}"
        )

        print(
            f"Showing rent popup: {player['name']} paid £{rent_amount} to {owner['name']}"
        )

    def show_tax_popup(self, player, tax_name, tax_amount):
        self.show_card = True
        self.current_card = {
            "type": "Tax Payment",
            "message": f"You landed on {tax_name}. Pay £{tax_amount} to the bank.",
        }
        self.current_card_player = player
        self.card_display_time = pygame.time.get_ticks()

        self.board.add_message(f"{player['name']} paid £{tax_amount} for {tax_name}")

        print(f"Showing tax popup: {player['name']} paid £{tax_amount} for {tax_name}")

    def handle_card_draw(self, player, card_type):

        result, message = self.logic.handle_card_draw(player, card_type)

        if result == "moved":
            player_obj = next(
                (p for p in self.players if p.name == player["name"]), None
            )
            if player_obj:
                player_obj.start_move([player["position"]])
                self.wait_for_animations()
                self.board.update_board_positions()

                self.renderer.draw()
                pygame.display.flip()

        return result

    def check_one_player_remains(self):
        if not hasattr(self, "_previous_active_counts"):
            self._previous_active_counts = {"ui": 0, "logic": 0}

        for ui_player in self.players:
            player_in_logic = any(
                p["name"] == ui_player.name for p in self.logic.players
            )
            if (
                not player_in_logic
                and not ui_player.bankrupt
                and not ui_player.voluntary_exit
            ):
                print(
                    f"Player {ui_player.name} not found in game logic but exists in UI - marking as bankrupt"
                )
                ui_player.bankrupt = True

        active_player_objects = [
            p for p in self.players if not p.bankrupt and not p.voluntary_exit
        ]
        active_player_data = [
            p
            for p in self.logic.players
            if p["money"] > 0
            and not p.get("exited", False)
            and not p.get("bankrupt", False)
        ]

        if (
            len(active_player_objects) != self._previous_active_counts["ui"]
            or len(active_player_data) != self._previous_active_counts["logic"]
        ):
            print(f"\nActive player count changed:")
            print(
                f"UI players: {len(active_player_objects)} - {[p.name for p in active_player_objects]}"
            )
            print(
                f"Logic players: {len(active_player_data)} - {[p['name'] for p in active_player_data]}"
            )

            self._previous_active_counts["ui"] = len(active_player_objects)
            self._previous_active_counts["logic"] = len(active_player_data)

        if len(active_player_objects) <= 1 and len(active_player_data) <= 1:
            print("\nOne or fewer players remain active")

            if len(active_player_objects) == 1 and len(active_player_data) == 1:
                winner = active_player_objects[0]
                print(f"Last player standing: {winner.name}")
                self.game_over = True
                self.handle_game_over(winner.name)
            elif len(active_player_objects) == 0 and len(active_player_data) == 0:
                print("No active players remain - ending with no winner")
                self.game_over = True

            return True

        return False

    def check_time_limit(self):
        if not self.time_limit or not self.start_time:
            return False

        current_time = pygame.time.get_ticks()

        elapsed_time_ms = current_time - self.start_time - self.total_pause_time
        if self.game_paused:
            current_pause_duration = current_time - self.pause_start_time
            elapsed_time_ms -= current_pause_duration

        time_limit_ms = self.time_limit * 1000

        from src.Sound_Manager import sound_manager

        remaining_time_seconds = (time_limit_ms - elapsed_time_ms) // 1000

        if self.game_mode == "abridged" and self.time_limit:
            if remaining_time_seconds <= 60 and remaining_time_seconds > 0:
                if not hasattr(self, "_last_countdown_sound_time"):
                    self._last_countdown_sound_time = 0

                if remaining_time_seconds <= 10:
                    if current_time - self._last_countdown_sound_time >= 1000:
                        sound_manager.play_sound("countdown")
                        self._last_countdown_sound_time = current_time
                        self.board.add_message(
                            f"Time remaining: {remaining_time_seconds} seconds"
                        )
                elif remaining_time_seconds <= 30:
                    if current_time - self._last_countdown_sound_time >= 5000:
                        sound_manager.play_sound("countdown")
                        self._last_countdown_sound_time = current_time
                        self.board.add_message(
                            f"Time remaining: {remaining_time_seconds} seconds"
                        )
                elif remaining_time_seconds == 60:
                    if (
                        not hasattr(self, "_one_minute_warning_played")
                        or not self._one_minute_warning_played
                    ):
                        sound_manager.play_sound("jail")
                        self.board.add_message("WARNING: 1 minute remaining!")
                        self._one_minute_warning_played = True

        if elapsed_time_ms >= time_limit_ms:
            if (
                not hasattr(self, "_time_limit_notified")
                or not self._time_limit_notified
            ):
                minutes = self.time_limit // 60
                print(f"\n\n!!!TIME LIMIT REACHED!!!: {minutes} minutes have elapsed!")
                print("Game will end after all players complete their current lap...")

                sound_manager.play_sound("game_over")

                self.board.add_message(f"TIME'S UP! Game will end after this lap.")

                if (
                    self.state == "AUCTION"
                    and hasattr(self.logic, "current_auction")
                    and self.logic.current_auction
                ):
                    print("Time limit reached during auction - canceling auction")
                    if (
                        isinstance(self.logic.current_auction, dict)
                        and "property" in self.logic.current_auction
                    ):
                        property_name = self.logic.current_auction.get(
                            "property", {}
                        ).get("name", "Unknown")
                        print(f"Auction for {property_name} canceled due to time limit")
                    self.logic.current_auction = None

                print("Clearing UI states to continue the game...")
                self.state = "ROLL"
                self.popup_message = None

                self._time_limit_notified = True
                self.time_limit_reached = True

                self.final_lap = {}
                for player_name, lap in self.lap_count.items():
                    player_obj = next(
                        (p for p in self.players if p.name == player_name), None
                    )
                    if (
                        player_obj
                        and not player_obj.bankrupt
                        and not player_obj.voluntary_exit
                    ):
                        self.final_lap[player_name] = lap

                print("\n===== CURRENT GAME STATE =====")
                print(
                    f"Active players: {len([p for p in self.players if not p.bankrupt and not p.voluntary_exit])}"
                )
                print(f"Current lap counts: {self.final_lap}")
                print("Game will end after all players complete their current lap")

                print("\nCurrent Player Assets:")
                try:
                    for logic_player in self.logic.players:
                        player_name = logic_player["name"]
                        player_obj = next(
                            (p for p in self.players if p.name == player_name), None
                        )

                        if player_obj and player_obj.voluntary_exit:
                            assets = player_obj.final_assets
                            status = "Voluntarily Exited"
                        elif player_obj and player_obj.bankrupt:
                            assets = 0
                            status = "Bankrupt"
                        else:
                            try:
                                assets = self.game_actions.calculate_player_assets(
                                    logic_player
                                )
                                status = "Active"
                            except Exception as e:
                                print(
                                    f"Error calculating assets for {player_name}: {e}"
                                )
                                assets = logic_player.get("money", 0)
                                status = "Active (Fallback)"

                        print(f"  {player_name}: £{assets} ({status})")
                        print(f"  Lap count: {self.lap_count.get(player_name, 0)}")
                except Exception as e:
                    print(f"Error listing player assets: {e}")
                print("============================\n")

            if hasattr(self, "final_lap"):
                all_completed = True
                active_players = [
                    p.name
                    for p in self.players
                    if not p.bankrupt and not p.voluntary_exit
                ]

                for player_name in active_players:
                    if player_name in self.final_lap:
                        current_lap = self.lap_count.get(player_name, 0)
                        final_lap = self.final_lap.get(player_name, 0)

                        if current_lap <= final_lap:
                            all_completed = False
                            print(
                                f"Waiting for {player_name} to complete their turn (lap {current_lap}, final lap {final_lap})"
                            )
                            break

                if all_completed:
                    print("All players have completed their final lap - ending game")
                    self.game_over = True
                    return True
                else:
                    return False

            return False

        return False

    def end_full_game(self):
        active_players = [
            p for p in self.players if not p.bankrupt and not p.voluntary_exit
        ]
        winner = active_players[0] if active_players else None

        final_assets = {}

        for logic_player in self.logic.players:
            player_name = logic_player["name"]
            player_obj = next((p for p in self.players if p.name == player_name), None)

            if player_obj and player_obj.voluntary_exit:
                final_assets[player_name] = player_obj.final_assets
            else:
                final_assets[player_name] = self.game_actions.calculate_player_assets(
                    logic_player
                )

        print(f"End full game assets: {final_assets}")

        return {
            "winner": winner.name if winner else "No winner",
            "final_assets": final_assets,
            "bankrupted_players": [p.name for p in self.players if p.bankrupt],
            "voluntary_exits": [p.name for p in self.players if p.voluntary_exit],
            "tied_winners": [],
        }

    def end_abridged_game(self):
        self.popup_message = None
        self.state = "ROLL"
        self.game_over = True

        final_assets = {}

        for logic_player in self.logic.players:
            player_name = logic_player["name"]
            player_obj = next((p for p in self.players if p.name == player_name), None)

            if player_obj and player_obj.voluntary_exit:
                final_assets[player_name] = player_obj.final_assets
            else:
                final_assets[player_name] = self.game_actions.calculate_player_assets(
                    logic_player
                )

        active_players = [
            p for p in self.players if not p.bankrupt and not p.voluntary_exit
        ]

        if active_players:
            active_player_assets = {
                p.name: final_assets.get(p.name, 0) for p in active_players
            }

            if active_player_assets:
                max_assets = (
                    max(active_player_assets.values()) if active_player_assets else 0
                )
                players_with_max_assets = [
                    name
                    for name, assets in active_player_assets.items()
                    if assets == max_assets
                ]

                if len(players_with_max_assets) > 1:
                    winner_name = "Tie"
                    tied_winners = players_with_max_assets
                else:
                    winner_name = (
                        players_with_max_assets[0]
                        if players_with_max_assets
                        else "No winner"
                    )
                    tied_winners = []
            else:
                winner_name = "No winner"
                tied_winners = []
        else:
            winner_name = "No winner"
            tied_winners = []

        print(f"End game assets: {final_assets}")
        print(f"Winner: {winner_name}")
        print(f"Tied winners: {tied_winners}")

        return {
            "winner": winner_name,
            "final_assets": final_assets,
            "bankrupted_players": [p.name for p in self.players if p.bankrupt],
            "voluntary_exits": [p.name for p in self.players if p.voluntary_exit],
            "tied_winners": tied_winners,
            "lap_count": self.lap_count,
        }

    def move_player(self, player, spaces):
        try:
            if not isinstance(player.position, int) or not (1 <= player.position <= 40):
                print(
                    f"Warning: Invalid position {player.position} detected for {player.name} in move_player, resetting to position 1"
                )
                player.position = 1

            old_position = player.position

            if not isinstance(spaces, int):
                print(
                    f"Warning: Invalid spaces value {spaces} for {player.name}, defaulting to 0"
                )
                spaces = 0
            elif spaces < 0 or spaces > 40:
                print(
                    f"Warning: Spaces value {spaces} out of range for {player.name}, adjusting to valid range"
                )
                spaces = max(0, min(spaces, 40))

            new_position = (old_position + spaces) % 40
            if new_position == 0:
                new_position = 40

            if not (1 <= new_position <= 40):
                print(
                    f"Warning: Invalid new position {new_position} calculated for {player.name}, correcting"
                )
                new_position = max(1, min(new_position, 40))

            print(
                f"Player.move: {player.name} from {old_position} to {new_position} ({spaces} steps)"
            )

            path = []
            for i in range(1, spaces + 1):
                step_pos = (old_position + i) % 40
                if step_pos == 0:
                    step_pos = 40
                path.append(step_pos)

            if path:
                print(f"Generated move path for {player.name}: {path}")

            player.start_move(path)

            found = False
            for logic_player in self.logic.players:
                if logic_player["name"] == player.name:
                    logic_player["position"] = new_position
                    found = True
                    break

            if not found:
                print(
                    f"Warning: Could not find logic player for {player.name} during move_player"
                )

            return new_position
        except Exception as e:
            print(f"Error in move_player: {e}")
            return player.position

    def wait_for_animations(self):
        any_player_moving = any(player.is_moving for player in self.players)

        if not any_player_moving:
            return

        print(f"Animations in progress, delaying game state progression")

        for player in self.players:
            if player.is_moving:
                player.update_animation()

        self.renderer.draw()
        pygame.display.flip()

        self.waiting_for_animation = True

    def check_passing_go(self, player, old_position):
        new_position = player.position

        if new_position < old_position and not self.logic.is_going_to_jail:
            player_dict = next(
                p for p in self.logic.players if p["name"] == player.name
            )
            player_dict["money"] += 200
            self.logic.bank_money -= 200
            self.board.add_message(f"{player.name} collected £200 for passing GO")

    def synchronize_player_positions(self):
        try:
            for player in self.players:
                if player.bankrupt or player.voluntary_exit:
                    continue

                if not isinstance(player.position, int) or not (
                    1 <= player.position <= 40
                ):
                    player.position = 1

            for logic_player in self.logic.players:
                if not isinstance(logic_player.get("position"), int) or not (
                    1 <= logic_player.get("position", 0) <= 40
                ):
                    logic_player["position"] = 1

            for player in self.players:
                if player.bankrupt or player.voluntary_exit:
                    continue

                found = False
                for logic_player in self.logic.players:
                    if player.name == logic_player["name"]:
                        found = True

                        if player.position != logic_player["position"]:
                            if player.is_ai:
                                player.position = logic_player["position"]
                            else:
                                if abs(player.position - logic_player["position"]) <= 3:
                                    logic_player["position"] = player.position
                        break

                if not found and not player.bankrupt and not player.voluntary_exit:
                    print(
                        f"Warning: Player {player.name} exists in UI but not in game logic"
                    )

            for logic_player in self.logic.players:
                found = False
                for player in self.players:
                    if logic_player["name"] == player.name:
                        found = True
                        break

                if not found:
                    print(
                        f"Warning: Player {logic_player['name']} exists in game logic but not in UI"
                    )
        except Exception as e:
            print(f"Error in synchronize_player_positions: {e}")

    def synchronize_player_money(self):
        for player in self.players:
            for logic_player in self.logic.players:
                if player.name == logic_player["name"]:
                    if hasattr(player, "money") and player.money != logic_player.get(
                        "money", 0
                    ):
                        old_money = player.money
                        player.money = logic_player.get("money", 0)
                        print(
                            f"Money synchronized for {player.name}: {old_money} -> {player.money}"
                        )
                    break

    def synchronize_free_parking_pot(self):
        if hasattr(self.logic, "free_parking_fund"):
            self.free_parking_pot = self.logic.free_parking_fund

    def show_exit_confirmation(self):
        window_size = self.screen.get_size()

        overlay = pygame.Surface(window_size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))

        dialog_width = int(window_size[0] * 0.4)
        dialog_height = int(window_size[1] * 0.3)
        dialog_x = (window_size[0] - dialog_width) // 2
        dialog_y = (window_size[1] - dialog_height) // 2

        shadow_rect = pygame.Rect(
            dialog_x + 6, dialog_y + 6, dialog_width, dialog_height
        )
        shadow = pygame.Surface((dialog_width, dialog_height), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (*BLACK, 128), shadow.get_rect(), border_radius=15)

        button_width = 100
        button_height = 40
        button_spacing = 30
        total_width = (button_width * 2) + button_spacing
        start_x = dialog_x + (dialog_width - total_width) // 2
        button_y = dialog_y + dialog_height - 80

        yes_button = pygame.Rect(start_x, button_y, button_width, button_height)
        no_button = pygame.Rect(
            start_x + button_width + button_spacing,
            button_y,
            button_width,
            button_height,
        )

        title_text = self.font.render("Leave Game?", True, ERROR_COLOR)
        title_rect = title_text.get_rect(
            centerx=dialog_x + dialog_width // 2, top=dialog_y + 20
        )

        warning_text = self.small_font.render(
            "You will lose the game if you leave!", True, BLACK
        )
        warning_rect = warning_text.get_rect(
            centerx=dialog_x + dialog_width // 2, top=title_rect.bottom + 20
        )

        message_text = self.small_font.render(
            "Your properties will return to bank.", True, BLACK
        )
        message_rect = message_text.get_rect(
            centerx=dialog_x + dialog_width // 2, top=warning_rect.bottom + 10
        )

        yes_text = self.font.render("Yes", True, WHITE)
        no_text = self.font.render("No", True, WHITE)

        last_yes_hover = False
        last_no_hover = False

        def draw_dialog(force_redraw=False, yes_hover=False, no_hover=False):
            if force_redraw or yes_hover != last_yes_hover or no_hover != last_no_hover:
                screen_backup = self.screen.copy()

                self.screen.blit(overlay, (0, 0))

                self.screen.blit(shadow, shadow_rect)
                pygame.draw.rect(
                    self.screen,
                    WHITE,
                    (dialog_x, dialog_y, dialog_width, dialog_height),
                    border_radius=15,
                )
                self.screen.blit(title_text, title_rect)
                self.screen.blit(warning_text, warning_rect)
                self.screen.blit(message_text, message_rect)

                pygame.draw.rect(
                    self.screen,
                    BUTTON_HOVER if yes_hover else ERROR_COLOR,
                    yes_button,
                    border_radius=5,
                )
                pygame.draw.rect(
                    self.screen,
                    BUTTON_HOVER if no_hover else ACCENT_COLOR,
                    no_button,
                    border_radius=5,
                )

                yes_rect = yes_text.get_rect(center=yes_button.center)
                self.screen.blit(yes_text, yes_rect)

                no_rect = no_text.get_rect(center=no_button.center)
                self.screen.blit(no_text, no_rect)

                pygame.display.flip()
                return yes_hover, no_hover
            return last_yes_hover, last_no_hover

        last_yes_hover, last_no_hover = draw_dialog(force_redraw=True)

        waiting = True
        confirm_exit = False
        last_update_time = pygame.time.get_ticks()

        while waiting:
            current_time = pygame.time.get_ticks()

            if current_time - last_update_time < 16:
                pygame.time.wait(5)
                continue

            last_update_time = current_time

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if yes_button.collidepoint(event.pos):
                        confirm_exit = True
                        waiting = False
                    elif no_button.collidepoint(event.pos):
                        confirm_exit = False
                        waiting = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        confirm_exit = True
                        waiting = False
                    elif event.key == pygame.K_n or event.key == pygame.K_ESCAPE:
                        confirm_exit = False
                        waiting = False

                elif event.type == pygame.MOUSEMOTION:
                    mouse_pos = pygame.mouse.get_pos()
                    yes_hover = yes_button.collidepoint(mouse_pos)
                    no_hover = no_button.collidepoint(mouse_pos)
                    last_yes_hover, last_no_hover = draw_dialog(
                        force_redraw=False, yes_hover=yes_hover, no_hover=no_hover
                    )

        pygame.time.wait(100)

        self.renderer.draw()
        pygame.display.flip()

        return confirm_exit

    def check_and_trigger_ai_turn(self, recursion_depth=0):
        if recursion_depth > len(self.logic.players):
            print(
                "Maximum recursion depth reached in check_and_trigger_ai_turn, aborting"
            )
            return False

        if self.state != "ROLL" and self.state != "DEVELOPMENT":
            print(
                f"Not in ROLL or DEVELOPMENT state, skipping AI turn check. Current state: {self.state}"
            )
            return False

        if not self.logic.players:
            print("No players left in the game")
            return False

        if self.logic.current_player_index >= len(self.logic.players):
            print(
                f"Invalid current_player_index: {self.logic.current_player_index}, max: {len(self.logic.players) - 1}"
            )
            self.logic.current_player_index = 0

        current_player = self.logic.players[self.logic.current_player_index]

        if current_player.get("exited", False) or current_player.get("bankrupt", False):
            print(
                f"Current player {current_player['name']} has exited (exited: {current_player.get('exited', False)}, bankrupt: {current_player.get('bankrupt', False)}), moving to next player"
            )
            self.logic.current_player_index = (
                self.logic.current_player_index + 1
            ) % len(self.logic.players)
            return self.check_and_trigger_ai_turn(recursion_depth + 1)

        player_obj = next(
            (p for p in self.players if p.name == current_player["name"]), None
        )

        if not player_obj:
            print(f"Could not find Player object for {current_player['name']}")
            self.logic.current_player_index = (
                self.logic.current_player_index + 1
            ) % len(self.logic.players)
            return self.check_and_trigger_ai_turn(recursion_depth + 1)

        if player_obj.in_jail != current_player.get("in_jail", False):
            print(f"Synchronizing jail state for {player_obj.name}")
            player_obj.in_jail = current_player.get("in_jail", False)
            current_player["in_jail"] = player_obj.in_jail
            player_obj.jail_turns = current_player.get("jail_turns", 0)
            current_player["jail_turns"] = player_obj.jail_turns

        if player_obj.in_jail and player_obj.stay_in_jail:
            print(
                f"Player {current_player['name']} chose to stay in jail - skipping turn"
            )
            self.board.add_message(
                f"{current_player['name']} is staying in jail - skipping turn"
            )
            self.logic.current_player_index = (
                self.logic.current_player_index + 1
            ) % len(self.logic.players)
            return self.check_and_trigger_ai_turn(recursion_depth + 1)

        if player_obj.is_ai:
            print(
                f"Player {current_player['name']} is an AI - automatically triggering their turn"
            )
            self.current_player_is_ai = True
            pygame.time.delay(500)
            try:
                if player_obj.in_jail and current_player.get("in_jail", False):
                    print(
                        f"AI player {current_player['name']} is in jail - handling jail turn first"
                    )
                    jail_result = self.game_actions.handle_jail_turn(current_player)
                    if not jail_result:
                        print(
                            f"AI player {current_player['name']} stays in jail - moving to next player"
                        )
                        self.handle_turn_end()
                        return self.check_and_trigger_ai_turn(recursion_depth + 1)

                if self.state == "DEVELOPMENT" and self.dev_manager.is_active:
                    print(
                        f"AI player {current_player['name']} is in development mode - automatically handling development"
                    )
                    self.handle_turn_end()
                    return self.check_and_trigger_ai_turn(recursion_depth + 1)

                if self.state == "ROLL":
                    turn_result = self.game_actions.play_turn()
                    if turn_result:
                        print(
                            f"AI player {current_player['name']} completed their turn"
                        )
                        return True
                    return False

                return True
            except Exception as e:
                print(f"Error in AI turn for {current_player['name']}: {e}")
                self.logic.current_player_index = (
                    self.logic.current_player_index + 1
                ) % len(self.logic.players)
                return self.check_and_trigger_ai_turn(recursion_depth + 1)
        else:
            print(
                f"Player {current_player['name']} is not an AI - waiting for user input"
            )
            self.current_player_is_ai = False
            return False

    def update_ai_mood(self, ai_player_name, is_happy):

        ai_player_obj = next(
            (p for p in self.players if p.name == ai_player_name and p.is_ai), None
        )

        if not ai_player_obj:
            print(f"Warning: Could not find AI player object for {ai_player_name}")
            return False

        any_updated = False

        for player in self.players:
            if (
                player.is_ai
                and hasattr(player, "ai_controller")
                and hasattr(player.ai_controller, "update_mood")
            ):
                player.ai_controller.update_mood(is_happy)
                any_updated = True

        if any_updated:
            mood_text = "happier" if is_happy else "angrier"
            self.board.add_message(f"All AI players are getting {mood_text}!")
            return True

        return False

    def update_current_player(self):
        if self.logic.current_player_index >= len(self.logic.players):
            print(f"Invalid current player index: {self.logic.current_player_index}")
            if len(self.logic.players) > 0:
                self.logic.current_player_index = 0
            else:
                print("No players left in the game")
                return

        current_logic_player = self.logic.players[self.logic.current_player_index]

        if current_logic_player.get("exited", False):
            print(
                f"Current player {current_logic_player['name']} has exited, moving to next player"
            )
            self.logic.current_player_index = (
                self.logic.current_player_index + 1
            ) % len(self.logic.players)
            return self.update_current_player()

        current_player = next(
            (p for p in self.players if p.name == current_logic_player["name"]),
            None,
        )

        if not current_player or (
            hasattr(current_player, "voluntary_exit") and current_player.voluntary_exit
        ):
            print(
                f"Player {current_logic_player['name']} has no UI representation or has voluntarily exited"
            )
            if not current_logic_player.get("exited", False):
                print(
                    f"Marking player {current_logic_player['name']} as exited in game logic"
                )
                current_logic_player["exited"] = True
            self.logic.current_player_index = (
                self.logic.current_player_index + 1
            ) % len(self.logic.players)
            return self.update_current_player()

        self.current_player_is_ai = current_player and current_player.is_ai

        for name, emotion_ui in self.emotion_uis.items():
            if not self.current_player_is_ai:
                print(f"Showing emotion UI for {name} during human turn")
                emotion_ui.show()
            else:
                print(f"Hiding emotion UI for {name} during AI turn")
                emotion_ui.hide()

        if current_player:
            print(f"Current player: {current_player.name} (AI: {current_player.is_ai})")
            self.board.add_message(f"{current_player.name}'s turn")
            if (
                hasattr(current_player, "is_ai")
                and current_player.is_ai
                and hasattr(current_player, "ai_controller")
            ):
                print(f"AI type: {type(current_player.ai_controller).__name__}")
                if hasattr(current_player.ai_controller, "mood_modifier"):
                    print(f"Current mood: {current_player.ai_controller.mood_modifier}")

    def can_develop(self, player):
        return self.dev_manager.can_develop(player)

    def handle_turn_end(self):
        current_player = self.logic.players[self.logic.current_player_index]
        player_obj = next(
            (p for p in self.players if p.name == current_player["name"]), None
        )
        is_ai_player = player_obj and player_obj.is_ai

        print(f"\n=== DEVELOPMENT MODE DEBUG - Turn End ===")
        print(f"Player: {current_player['name']}")
        print(f"Current development_mode: {self.development_mode}")
        print(f"Lap count: {self.lap_count.get(current_player['name'], 0)}")
        print(f"Current state: {self.state}")
        print(f"Is AI player: {is_ai_player}")

        owned_properties = [
            prop
            for prop in self.logic.properties.values()
            if prop.get("owner") == current_player["name"]
        ]
        print(f"Owned properties: {len(owned_properties)}")
        for prop in owned_properties:
            print(f"  - {prop['name']} (Group: {prop.get('group', 'None')})")

        can_develop_properties = self.can_develop(current_player)
        print(f"Can develop properties: {can_develop_properties}")

        if (
            is_ai_player
            and not self.development_mode
            and self.can_develop(current_player)
        ):
            print(
                f"AI player {current_player['name']} could develop properties but chose not to"
            )

        if self.development_mode:
            print(f"Ending development phase for {current_player['name']}")
            self.development_mode = False
            print(f"Development mode set to: {self.development_mode}")
        elif (
            not is_ai_player
            and not self.development_mode
            and self.can_develop(current_player)
        ):
            print(
                f"Human player {current_player['name']} can develop - entering development mode"
            )
            self.state = "DEVELOPMENT"
            self.development_mode = True

            activated = self.dev_manager.activate(current_player)

            if not activated:
                print(
                    "WARNING: Development mode state set, but dev_manager failed to activate!"
                )
                self.state = "ROLL"
                self.development_mode = False
                self.logic.current_player_index = (
                    self.logic.current_player_index + 1
                ) % len(self.logic.players)
                print(
                    f"Moving to next player due to failed activation, new index: {self.logic.current_player_index}"
                )
                self.update_current_player()
                return

            print(
                f"Development mode set to: {self.development_mode}, DevManager active: {self.dev_manager.is_active}"
            )

            print(f"\n=== Properties eligible for development ===")
            for prop in owned_properties:
                can_build_house, house_error = self.logic.can_build_house(
                    prop, current_player
                )
                can_build_hotel, hotel_error = self.logic.can_build_hotel(
                    prop, current_player
                )
                print(f"  - {prop['name']} (Houses: {prop.get('houses', 0)})")
                print(
                    f"    Can build house: {can_build_house} {'' if can_build_house else '- ' + (house_error or 'Unknown error')}"
                )
                print(
                    f"    Can build hotel: {can_build_hotel} {'' if can_build_hotel else '- ' + (hotel_error or 'Unknown error')}"
                )

            self.renderer.draw()
            pygame.display.flip()
            return
        else:
            print(f"No development phase needed for {current_player['name']}")
            self.development_mode = False
            print(f"Development mode set to: {self.development_mode}")
            self.logic.current_player_index = (
                self.logic.current_player_index + 1
            ) % len(self.logic.players)
            print(
                f"Moving to next player, new index: {self.logic.current_player_index}"
            )
            self.update_current_player()

        self.state = "ROLL"
        self.current_property = None
        self.last_roll = None
        self.roll_time = 0
        self.dice_animation = False
        self.dice_values = None

        self.renderer.draw()
        pygame.display.flip()
        print(f"Final state after turn end: {self.state}")

    def handle_key(self, event):
        if self.dev_manager.is_active:
            if (
                hasattr(self.dev_manager, "notification")
                and self.dev_manager.notification
            ):
                if self.dev_manager.notification.handle_key(event):
                    self.dev_manager.deactivate()
                    return False
            return self.dev_manager.handle_key(event)

        if self.show_popup:
            if event.key in [pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE]:
                self.show_popup = False
                return False

        if self.show_card:
            if event.key in [pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE]:
                self.show_card = False
                self.current_card = None
                self.current_card_player = None
                return False

        for emotion_ui in self.emotion_uis.values():
            if emotion_ui.handle_key(event):
                return False

        any_player_moving = any(player.is_moving for player in self.players)
        if any_player_moving and event.key not in [
            pygame.K_LEFT,
            pygame.K_RIGHT,
            pygame.K_UP,
            pygame.K_DOWN,
        ]:
            print("Animations in progress, ignoring key input")
            return False
