# Property Tycoon GameActions.py
# It contains the classes for the game actions, such as the play turn, the handle buy decision, and the start auction.

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
from src.Sound_Manager import sound_manager
from src.Ai_Player_Logic import EasyAIPlayer, HardAIPlayer
from typing import Optional
import string
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
ACCENT_COLOR = BURGUNDY
BUTTON_HOVER = (160, 20, 40)
ERROR_COLOR = (220, 53, 69)
SUCCESS_COLOR = DARK_GREEN
MODE_COLOR = DARK_BLUE
TIME_COLOR = (255, 180, 100)
HUMAN_COLOR = DARK_GREEN
AI_COLOR = DARK_RED


class GameActions:
    def __init__(self, game):
        self.game = game

    def play_turn(self):
        if self.game.game_over:
            return False

        if self.game.dice_animation:
            return False

        if any(player.is_moving for player in self.game.players):
            return False

        current_player = self.game.logic.players[self.game.logic.current_player_index]
        if not current_player:
            self.game.board.add_message("Error: No current player found")
            return False

        player_obj = next(
            (p for p in self.game.players if p.name == current_player["name"]), None
        )
        is_ai_player = player_obj and player_obj.is_ai

        if self.game.development_mode and not is_ai_player:
            return False

        self.game.update_current_player()

        if not player_obj:
            print(f"Warning: Could not find player object for {current_player['name']}")
            return False

        if player_obj.in_jail != current_player.get("in_jail", False):
            print(f"Synchronizing jail status for {player_obj.name}")
            player_obj.in_jail = current_player.get("in_jail", False)
            current_player["in_jail"] = player_obj.in_jail
            player_obj.jail_turns = current_player.get("jail_turns", 0)
            current_player["jail_turns"] = player_obj.jail_turns

        if player_obj.in_jail and player_obj.stay_in_jail:
            print(
                f"Player {current_player['name']} chose to stay in jail - skipping turn"
            )
            self.game.board.add_message(
                f"{current_player['name']} is staying in jail - skipping turn"
            )
            self.game.handle_turn_end()
            return True

        if player_obj.in_jail and current_player.get("in_jail", False):
            print(f"Player {current_player['name']} is in jail - showing jail options")
            jail_result = self.handle_jail_turn(current_player)
            if not jail_result:
                self.game.board.add_message(f"{current_player['name']} stays in jail")
                self.game.handle_turn_end()
                return True

        old_position = current_player["position"]

        self.game.lap_count[current_player["name"]] += 1
        print(
            f"Lap count for {current_player['name']}: {self.game.lap_count[current_player['name']]}"
        )

        if self.game.state == "ROLL":
            self.game.dice_animation = True
            self.game.animation_start = pygame.time.get_ticks()

            sound_manager.play_sound("dice_roll")

            dice1, dice2 = self.game.logic.play_turn()
            if dice1 is None:
                self.game.dice_animation = False
                return True

            while self.game.logic.message_queue:
                message = self.game.logic.message_queue.pop(0)
                print(f"Processing message: {message}")
                self.game.board.add_message(message)
                if "left jail" in message:
                    print(f"Jail exit notification: {message}")
                    sound_manager.play_sound("jail")

            self.game.dice_values = (dice1, dice2)

            for player in self.game.players:
                if player.name == current_player["name"]:
                    if player.position != old_position:
                        print(
                            f"Correcting position mismatch for {player.name}: Player object: {player.position}, Game logic: {old_position}"
                        )
                        player.position = old_position

                    spaces_to_move = (current_player["position"] - old_position) % 40
                    if (
                        spaces_to_move == 0
                        and current_player["position"] != old_position
                    ):
                        spaces_to_move = 40

                    self.game.move_player(player, spaces_to_move)
                    print(
                        f"Starting animation for {player.name} to move {spaces_to_move} spaces from {old_position} to {current_player['position']}"
                    )

        self.game.wait_for_animations()

        self.game.board.update_board_positions()

        if current_player["position"] < old_position:
            self.game.rounds_completed[current_player["name"]] += 1
            self.game.board.add_message("*** PASSED GO! ***")
            self.game.board.add_message(f"{current_player['name']} collected £200")
            sound_manager.play_sound("collect_money")

        self.game.board.add_message(f"{current_player['name']} rolled {dice1 + dice2}")

        if dice1 == dice2:
            self.game.board.add_message("Doubles! Roll again!")

        self.game.renderer.draw()
        pygame.display.flip()

        if self.game.check_game_over():
            return True

        return False

    def handle_buy_decision(self, wants_to_buy):
        current_player = self.game.logic.players[self.game.logic.current_player_index]
        property_data = self.game.current_property

        print("\n=== Property Purchase Debug ===")
        print(f"Current state: {self.game.state}")
        print(f"Player: {current_player['name']}")
        print(f"Player money: £{current_player['money']}")
        print(f"Property: {property_data['name']}")
        print(f"Property price: £{property_data['price']}")
        print(f"Wants to buy: {wants_to_buy}")
        print(f"Is AI: {self.game.current_player_is_ai}")
        print(
            f"Completed circuits: {self.game.logic.completed_circuits.get(current_player['name'], 0)}"
        )
        print(
            f"Current lap count: {self.game.lap_count.get(current_player['name'], 0)}"
        )

        print(f"Property owner before: {property_data.get('owner', 'None')}")

        if wants_to_buy:
            if current_player["money"] >= property_data["price"]:
                print("\nAttempting purchase...")
                current_player["money"] -= property_data["price"]
                property_data["owner"] = current_player["name"]
                print(f"Property owner set to: {property_data['owner']}")
                print(f"Property data position: {property_data['position']}")
                print(
                    f"Property in self.game.logic.properties: {property_data['position'] in self.game.logic.properties}"
                )

                if str(property_data["position"]) in self.game.logic.properties:
                    print(
                        f"Global property owner: {self.game.logic.properties[str(property_data['position'])].get('owner', 'None')}"
                    )
                    self.game.logic.properties[str(property_data["position"])][
                        "owner"
                    ] = current_player["name"]
                    print(
                        f"Updated global property owner: {self.game.logic.properties[str(property_data['position'])].get('owner', 'None')}"
                    )

                self.game.board.add_message(
                    f"{current_player['name']} bought {property_data['name']} for £{property_data['price']}"
                )
                print("Purchase successful")

                sound_manager.play_sound("buy_property")

                if (
                    not hasattr(self.game.logic, "current_auction")
                    or not self.game.logic.current_auction
                ):
                    print("State changed to ROLL")
                    self.game.state = "ROLL"
                else:
                    print("Auction in progress - maintaining AUCTION state")

                print("\nPlayer properties after purchase:")
                owned_count = 0
                for prop_pos, prop in self.game.logic.properties.items():
                    if prop.get("owner") == current_player["name"]:
                        owned_count += 1
                        print(
                            f"  - {prop['name']} (Position: {prop_pos}, Group: {prop.get('group', 'None')})"
                        )
                print(f"Total properties owned: {owned_count}")

                self.game.board.update_ownership(self.game.logic.properties)

                self.game.renderer.draw()
                pygame.display.flip()
            else:
                print("\nNot enough money for purchase")
                self.game.board.add_message(
                    f"{current_player['name']} doesn't have enough money to buy {property_data['name']}"
                )

                print("Starting auction due to insufficient funds")
                self.start_auction(property_data)
        else:
            print("\nPlayer passed on purchase")
            self.start_auction(property_data)

        print("\nFinal state:")
        print(f"Property owner: {property_data['owner']}")
        print(f"Player money: £{current_player['money']}")

        if (
            not hasattr(self.game.logic, "current_auction")
            or not self.game.logic.current_auction
        ):
            print(f"Final state: {self.game.state}")
            if self.game.state == "ROLL":
                self.game.update_current_player()
        else:
            print(f"Auction in progress - state is {self.game.state}")

        self.game.renderer.draw()
        pygame.display.flip()

    def start_auction(self, property_data):
        print(f"\n=== Starting Auction for {property_data['name']} ===")

        any_eligible = False
        for player in self.game.logic.players:
            if self.game.logic.completed_circuits.get(player["name"], 0) >= 1:
                any_eligible = True
                break

        if not any_eligible:
            print("No players have completed a circuit - skipping auction")
            message = "No players have completed a circuit - property remains unsold"
            self.game.board.add_message(message)
            self.game.state = "ROLL"
            self.game.renderer.draw()
            pygame.display.flip()
            self.game.update_current_player()
            return

        any_moving = any(player.is_moving for player in self.game.players)
        if any_moving:
            print("Animations in progress - delaying auction start")
            self.game.pending_auction_property = property_data
            self.game.waiting_for_animation = True
            return

        active_players = [
            p["name"]
            for p in self.game.logic.players
            if not p.get("bankrupt", False) and not p.get("exited", False)
        ]
        if len(active_players) == 1:
            print(f"Only one active player ({active_players[0]}) - skipping auction")
            self.game.state = "ROLL"
            self.game.renderer.draw()
            pygame.display.flip()
            self.game.update_current_player()
            return

        result = self.game.logic.auction_property(property_data["position"])

        if result == "auction_in_progress":
            self.game.state = "AUCTION"
            self.game.auction_bid_amount = ""
            print(f"State changed to {self.game.state}")
            self.game.auction_just_started = True
            self.game.board.add_message(f"Auction for {property_data['name']} started!")

            self.game.renderer.draw()
            pygame.display.flip()
        else:
            print(f"Failed to start auction: {result}")
            self.game.state = "ROLL"
            print(f"State changed to {self.game.state}")
            self.game.renderer.draw()
            pygame.display.flip()
            self.game.update_current_player()

        print(f"Final state: {self.game.state}")
        print("=== End Auction ===\n")

    def handle_jail_turn(self, player):
        print(f"\n=== Jail Turn Handler for {player['name']} ===")
        print(f"In jail: {player['in_jail']}")
        print(f"Jail turns: {player.get('jail_turns', 0)}")
        print(f"Money: £{player['money']}")
        print(
            f"Has jail free cards: {self.game.logic.jail_free_cards.get(player['name'], 0)}"
        )

        if not player["in_jail"]:
            print("Player not in jail - exiting jail handler")
            return False

        player_obj = next(
            (p for p in self.game.players if p.name == player["name"]), None
        )
        if not player_obj:
            print(f"Warning: Could not find player object for {player['name']}")
            return False

        if not player_obj.in_jail:
            print(f"Synchronizing jail state for {player['name']}")
            player_obj.in_jail = True
            player_obj.jail_turns = player["jail_turns"]

        if player_obj.is_ai:
            print(f"AI player {player['name']} deciding how to handle jail")

            if self.game.logic.jail_free_cards.get(player["name"], 0) > 0:
                print(f"AI using 'Get Out of Jail Free' card")
                card_type = player_obj.use_jail_card()
                if card_type == CardType.POT_LUCK:
                    self.game.pot_luck_deck.return_jail_card(card_type)
                    print("Returned Pot Luck jail card to deck")
                else:
                    self.game.opportunity_deck.return_jail_card(card_type)
                    print("Returned Opportunity Knocks jail card to deck")

                player["in_jail"] = False
                player["jail_turns"] = 0
                player_obj.in_jail = False
                player_obj.jail_turns = 0
                player_obj.stay_in_jail = False
                self.game.board.add_message(
                    f"{player['name']} used Get Out of Jail Free card and left jail!"
                )
                print(f"AI player {player['name']} successfully left jail using card")
                return True
            elif player["money"] >= 50 and random.random() < 0.5:
                print(
                    f"AI player {player['name']} paying £50 to leave jail (randomly decided)"
                )
                player["money"] -= 50
                self.game.logic.free_parking_fund += 50
                self.game.synchronize_free_parking_pot()
                player["in_jail"] = False
                player["jail_turns"] = 0
                player_obj.in_jail = False
                player_obj.jail_turns = 0
                player_obj.stay_in_jail = False
                self.game.board.add_message(f"{player['name']} paid £50 and left jail!")
                print(
                    f"AI player {player['name']} successfully left jail by paying £50"
                )
                return True
            else:
                print(f"AI player {player['name']} will try to roll doubles")
        else:
            print(f"Human player {player['name']} choosing jail option")
            self.game.renderer.draw()
            pygame.display.flip()

            choice = self.game.get_jail_choice(player)
            print(f"Human player selected option: {choice}")

            if (
                choice == "card"
                and self.game.logic.jail_free_cards.get(player["name"], 0) > 0
            ):
                print(f"Using 'Get Out of Jail Free' card")
                card_type = player_obj.use_jail_card()
                if card_type == CardType.POT_LUCK:
                    self.game.pot_luck_deck.return_jail_card(card_type)
                else:
                    self.game.opportunity_deck.return_jail_card(card_type)
                player["in_jail"] = False
                player["jail_turns"] = 0
                player_obj.in_jail = False
                player_obj.jail_turns = 0
                player_obj.stay_in_jail = False
                self.game.board.add_message(
                    f"{player['name']} used Get Out of Jail Free card and left jail!"
                )
                print(f"Player {player['name']} successfully left jail using card")
                return True
            elif choice == "pay" and player["money"] >= 50:
                print(f"Paying £50 to leave jail")
                player["money"] -= 50
                self.game.logic.free_parking_fund += 50
                self.game.synchronize_free_parking_pot()
                player["in_jail"] = False
                player["jail_turns"] = 0
                player_obj.in_jail = False
                player_obj.jail_turns = 0
                player_obj.stay_in_jail = False
                self.game.board.add_message(f"{player['name']} paid £50 and left jail!")
                try:
                    self.game.board.add_message(
                        f"{player['name']} paid £50 and left jail!"
                    )
                except AttributeError:
                    print("Error: board.add_message call failed")
                print(f"Player {player['name']} successfully left jail by paying £50")
                return True
            elif choice == "stay":
                print(f"Player {player['name']} chose to stay in jail")
                player_obj.stay_in_jail = True
                player["jail_turns"] = player.get("jail_turns", 0) + 1
                player_obj.jail_turns = player["jail_turns"]
                self.game.board.add_message(f"{player['name']} chose to stay in jail!")
                return False
            elif choice == "roll":
                print(f"Player {player['name']} will try to roll doubles")
                return True

        player["jail_turns"] = player.get("jail_turns", 0) + 1
        player_obj.jail_turns = player["jail_turns"]
        print(f"Jail turn count increased to {player['jail_turns']}")

        if player["jail_turns"] >= 3:
            print(f"Player {player['name']} has been in jail for 3 turns")
            if player["money"] >= 50:
                print("Forcing payment after 3 turns")
                player["money"] -= 50
                self.game.logic.free_parking_fund += 50
                self.game.synchronize_free_parking_pot()
                player["in_jail"] = False
                player["jail_turns"] = 0
                player_obj.in_jail = False
                player_obj.jail_turns = 0
                player_obj.stay_in_jail = False
                self.game.board.add_message(
                    f"{player['name']} paid £50 after 3 turns and left jail!"
                )
                print(
                    f"Player {player['name']} successfully left jail after 3 turns by paying £50"
                )
                return True
            else:
                print(
                    f"Player {player['name']} can't pay jail fine - leaving jail bankrupt"
                )
                player["in_jail"] = False
                player["jail_turns"] = 0
                player_obj.in_jail = False
                player_obj.jail_turns = 0
                player_obj.stay_in_jail = False
                self.game.board.add_message(
                    f"{player['name']} couldn't pay jail fine and left jail bankrupt!"
                )
                self.handle_bankruptcy(player)
                return True

        print(f"Player {player['name']} remains in jail - jail turn handled\n")
        return False

    def handle_voluntary_exit(self, player_name, final_assets):
        print(f"\n=== Voluntary Exit Debug ===")
        print(f"Player {player_name} is exiting the game")

        logic_player = next(
            (p for p in self.game.logic.players if p["name"] == player_name), None
        )
        if logic_player:
            actual_final_assets = self.calculate_player_assets(logic_player)
            print(f"Final assets calculated from game logic: {actual_final_assets}")
        else:
            actual_final_assets = final_assets
            print(f"Using provided final assets: {final_assets}")

        print(f"Current number of players: {len(self.game.logic.players)}")
        print(
            f"Current player index before exit: {self.game.logic.current_player_index}"
        )

        self.game.board.add_message(f"{player_name} exits game")

        player_obj = next((p for p in self.game.players if p.name == player_name), None)
        if not player_obj:
            print(f"Error: Could not find player object for {player_name}")
            return False

        print(f"Found player object: {player_obj.name}")

        player_properties = [
            p
            for p in self.game.logic.properties.values()
            if p.get("owner") == player_name
        ]
        print(
            f"Player has {len(player_properties)} properties that will be returned to bank"
        )

        if hasattr(player_obj, "handle_voluntary_exit"):
            print(f"Setting voluntary_exit flag for {player_name}")
            player_obj.final_assets = actual_final_assets
            player_obj.handle_voluntary_exit()

        result = self.game.logic.remove_player(player_name, voluntary=True)
        print(f"Game logic marked player as exited: {result}")

        if result:
            exited_player = next(
                (p for p in self.game.logic.players if p["name"] == player_name), None
            )
            if exited_player and exited_player.get("exited", False):
                print(f"Player {player_name} successfully marked as exited")
            else:
                print(f"Warning: Player {player_name} not properly marked as exited")

            self.game.board.update_ownership(self.game.logic.properties)

            active_players = [
                p for p in self.game.logic.players if not p.get("exited", False)
            ]
            print(f"Active players after exit: {[p['name'] for p in active_players]}")

            next_player_found = False
            original_index = self.game.logic.current_player_index

            while not next_player_found and active_players:
                self.game.logic.current_player_index = (
                    self.game.logic.current_player_index + 1
                ) % len(self.game.logic.players)

                if self.game.logic.current_player_index == original_index:
                    break

                current_player = self.game.logic.players[
                    self.game.logic.current_player_index
                ]
                if not current_player.get("exited", False):
                    next_player_found = True
                    print(
                        f"Next active player: {current_player['name']} (index: {self.game.logic.current_player_index})"
                    )

            print(
                f"Current player index after exit: {self.game.logic.current_player_index}"
            )

            if len(active_players) <= 1:
                print(
                    f"Only {len(active_players)} active player(s) left - game should end soon"
                )
                if self.game.check_one_player_remains():
                    print("Game ending due to only one player remaining")
                    game_over_data = self.end_full_game()
                    return game_over_data

            self.game.state = "ROLL"
            print("Checking if next player is an AI...")
            self.game.check_and_trigger_ai_turn()

            return True
        else:
            print("Failed to mark player as exited in game logic")
            return False

    def calculate_player_assets(self, player):
        try:
            if not player or not isinstance(player, dict):
                print(
                    f"Warning: Invalid player object in calculate_player_assets: {player}"
                )
                return 0

            total = player.get("money", 0)

            if (
                not hasattr(self.game.logic, "properties")
                or not self.game.logic.properties
            ):
                print("Warning: No properties found in game logic")
                return total

            for prop_id, prop in self.game.logic.properties.items():
                if not isinstance(prop, dict):
                    continue

                if prop.get("owner") == player.get("name"):
                    total += prop.get("price", 0)

                    if "houses" in prop and prop["houses"] > 0:
                        house_costs = prop.get("house_costs", [])

                        if isinstance(house_costs, list) and house_costs:
                            houses_count = min(prop["houses"], len(house_costs))
                            for i in range(houses_count):
                                total += house_costs[i]
                        elif isinstance(house_costs, (int, float)):
                            total += house_costs * prop["houses"]

            return total

        except Exception as e:
            print(f"Error in calculate_player_assets: {e}")
            return player.get("money", 0)

    def handle_ai_turn(self, ai_player):
        MAX_ITERATIONS = 100
        iteration_count = 0

        try:
            player_obj = next(
                (
                    player
                    for player in self.game.players
                    if player.name == ai_player["name"]
                ),
                None,
            )

            if not player_obj:
                return None

            if not player_obj.is_ai:
                return None

            player_pos_valid = (
                isinstance(player_obj.position, int) and 1 <= player_obj.position <= 40
            )
            logic_pos_valid = (
                isinstance(ai_player.get("position"), int)
                and 1 <= ai_player.get("position", 0) <= 40
            )

            if not player_pos_valid and logic_pos_valid:
                player_obj.position = ai_player["position"]
            elif player_pos_valid and not logic_pos_valid:
                ai_player["position"] = player_obj.position
            elif not player_pos_valid and not logic_pos_valid:
                player_obj.position = 1
                ai_player["position"] = 1
            elif player_obj.position != ai_player["position"]:
                player_obj.position = ai_player["position"]
        except Exception as e:
            return None

        if self.game.state == "ROLL":
            self.play_turn()

            start_time = pygame.time.get_ticks()
            while self.game.state == "BUY" and self.game.current_property:

                current_time = pygame.time.get_ticks()
                if current_time - start_time > 5000:
                    print(
                        f"Timeout reached for AI {ai_player['name']} in BUY state - forcing decision"
                    )
                    self.handle_buy_decision(False)
                    break

                iteration_count += 1
                if iteration_count > MAX_ITERATIONS:
                    print(
                        f"Maximum iterations reached for AI {ai_player['name']} in BUY state - forcing decision"
                    )
                    self.handle_buy_decision(False)
                    break

                print(f"\n=== AI Purchase Decision ===")
                print(f"AI Player: {ai_player['name']}")
                print(f"Property: {self.game.current_property['name']}")
                print(f"Price: £{self.game.current_property['price']}")
                print(f"AI Money: £{ai_player['money']}")

                try:
                    should_buy = self.game.logic.ai_player.should_buy_property(
                        self.game.current_property,
                        ai_player["money"],
                        [
                            p
                            for p in self.game.logic.properties.values()
                            if p.get("owner") == ai_player["name"]
                        ],
                    )

                    if should_buy:
                        print("AI Decision: Buy")
                        self.handle_buy_decision(True)
                    else:
                        print("AI Decision: Pass")
                        self.handle_buy_decision(False)
                except Exception as e:
                    print(f"Error in AI purchase decision: {e}")
                    self.handle_buy_decision(False)
                break

        elif self.game.state == "AUCTION" and hasattr(
            self.game.logic, "current_auction"
        ):
            auction_data = self.game.logic.current_auction

            if auction_data is None:
                print("Warning: Auction data is None in handle_ai_turn")
                return None

            start_time = pygame.time.get_ticks()
            while (
                auction_data["active_players"][auction_data["current_bidder_index"]][
                    "name"
                ]
                == ai_player["name"]
            ):
                current_time = pygame.time.get_ticks()
                if current_time - start_time > 5000:
                    print(
                        f"Timeout reached for AI {ai_player['name']} in AUCTION state - forcing pass"
                    )
                    success, message = self.game.logic.process_auction_pass(ai_player)
                    if message:
                        self.game.board.add_message(message)
                    break

                iteration_count += 1
                if iteration_count > MAX_ITERATIONS:
                    print(
                        f"Maximum iterations reached for AI {ai_player['name']} in AUCTION state - forcing pass"
                    )
                    success, message = self.game.logic.process_auction_pass(ai_player)
                    if message:
                        self.game.board.add_message(message)
                    break

                print(f"\n=== AI Auction Turn ===")
                print(f"AI Player: {ai_player['name']}")
                print(f"Property: {auction_data['property']['name']}")
                print(f"Current bid: £{auction_data['current_bid']}")
                print(f"Minimum bid: £{auction_data['minimum_bid']}")

                if ai_player["name"] in auction_data.get("passed_players", set()):
                    print(f"AI {ai_player['name']} has already passed")
                    break

                try:
                    bid_amount = self.game.logic.get_ai_auction_bid(
                        ai_player, auction_data["property"], auction_data["current_bid"]
                    )

                    if bid_amount and bid_amount >= auction_data["minimum_bid"]:
                        print(f"AI Decision: Bid £{bid_amount}")
                        success, message = self.game.logic.process_auction_bid(
                            ai_player, bid_amount
                        )
                        if message:
                            self.game.board.add_message(message)
                    else:
                        print("AI Decision: Pass")
                        success, message = self.game.logic.process_auction_pass(
                            ai_player
                        )
                        if message:
                            self.game.board.add_message(message)
                except Exception as e:
                    print(f"Error in AI auction decision: {e}")
                    success, message = self.game.logic.process_auction_pass(ai_player)
                    if message:
                        self.game.board.add_message(message)

                result_message = self.game.logic.check_auction_end()
                if result_message:
                    self.game.board.add_message(result_message)
                    self.game.state = "ROLL"
                    self.game.board.update_ownership(self.game.logic.properties)
                break

        return None

    def handle_bankruptcy(self, player):
        for ui_player in self.game.players:
            if ui_player.name == player["name"]:
                ui_player.bankrupt = True
                print(f"Marking player {ui_player.name} as bankrupt in UI")
                break

        if self.game.logic.remove_player(player["name"]):
            self.game.board.add_message(f"{player['name']} bankrupt!")
            self.game.board.update_ownership(self.game.logic.properties)

            if self.game.check_one_player_remains():
                print("Only one player remains after bankruptcy - ending game")
                if (
                    hasattr(self.game, "game_settings")
                    and self.game.game_settings.get("mode") == "full"
                ):
                    self.end_full_game()
                else:
                    self.end_abridged_game()

            return True
        return False

    def add_to_free_parking(self, amount):
        self.game.free_parking_pot += amount
        self.game.board.add_message(
            f"£{amount} added to Free Parking pot (Total: £{self.game.free_parking_pot})"
        )

    def collect_free_parking(self, player):
        if self.game.free_parking_pot > 0:
            amount = self.game.free_parking_pot
            player["money"] += amount
            self.game.free_parking_pot = 0
            self.game.logic.free_parking_fund = 0
            self.game.board.add_message(
                f"{player['name']} collected £{amount} from Free Parking!"
            )

            self.game.show_card = True
            self.game.current_card = {
                "type": "Free Parking",
                "message": f"You collected £{amount:,} from the Free Parking pot!",
            }
            self.game.current_card_player = player
            self.game.card_display_time = pygame.time.get_ticks()

            pygame.event.clear()
            waiting = True
            while waiting:
                self.game.renderer.draw()
                pygame.display.flip()

                for event in pygame.event.get():
                    if event.type in [pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN]:
                        waiting = False
                        self.game.show_card = False
                        self.game.current_card = None
                        self.game.current_card_player = None
                    elif event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                pygame.time.wait(30)

            return True
        return False

    def handle_fine_payment(self, player, amount, reason="fine"):
        if player["money"] >= amount:
            player["money"] -= amount
            self.add_to_free_parking(amount)
            self.game.board.add_message(f"{player['name']} paid £{amount} {reason}")
            return True
        else:
            self.game.board.add_message(
                f"{player['name']} cannot pay £{amount} {reason}"
            )
            return False

    def show_time_stats(self):
        if self.game.game_mode == "abridged" and self.game.time_limit:
            current_time = pygame.time.get_ticks()
            elapsed = (current_time - self.game.start_time) // 1000
            remaining = max(0, self.game.time_limit - elapsed)
            minutes = remaining // 60
            seconds = remaining % 60

            self.game.board.add_message(f"Time: {minutes:02d}:{seconds:02d}")

            min_rounds = min(self.game.rounds_completed.values())
            max_rounds = max(self.game.rounds_completed.values())
            if min_rounds != max_rounds:
                self.game.board.add_message(f"Rounds: {min_rounds}-{max_rounds}")

    def show_exit_confirmation(self):
        return self.game.show_exit_confirmation()

    def check_one_player_remains(self):
        return self.game.check_one_player_remains()

    def check_game_over(self):
        return self.game.check_game_over()

    def check_and_trigger_ai_turn(self):
        return self.game.check_and_trigger_ai_turn()

    def end_full_game(self):
        return self.game.end_full_game()

    def end_abridged_game(self):
        return self.game.end_abridged_game()
