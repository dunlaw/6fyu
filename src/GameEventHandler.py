# Property Tycoon GameEventHandler.py
# It contains the classes for the game event handler, such as the handle input, the handle click, and the handle motion.

import pygame
import sys
from src.Cards import CardType

KEY_ROLL = [pygame.K_SPACE, pygame.K_RETURN]
KEY_BUY = [pygame.K_y, pygame.K_RETURN]
KEY_PASS = [pygame.K_n, pygame.K_ESCAPE]


class GameEventHandler:
    def __init__(self, game, game_actions):
        self.game = game
        self.game_actions = game_actions

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    result = self.handle_click(event.pos)
                    if result == True:
                        return "game_over"
                    elif isinstance(result, dict) and "winner" in result:
                        return result
            elif event.type == pygame.MOUSEMOTION:
                self.handle_motion(event.pos)
            elif event.type == pygame.KEYDOWN:
                result = self.handle_key(event)
                if result == True:
                    return "game_over"
                elif isinstance(result, dict) and "winner" in result:
                    return result
        return None

    def handle_click(self, pos):
        if self.game.game_over:
            return False

        if self.game.dev_manager.is_active:
            return self.game.dev_manager.handle_click(pos)

        for emotion_ui in self.game.emotion_uis.values():
            if emotion_ui.handle_click(pos):
                return False

        if self.game.show_popup:
            if self.game.popup_rect.collidepoint(pos):
                self.game.show_popup = False
            return False

        if self.game.show_card:
            self.game.show_card = False
            self.game.current_card = None
            self.game.current_card_player = None
            return False

        any_player_moving = any(player.is_moving for player in self.game.players)
        if any_player_moving:
            print("Animations in progress, delaying game state progression")
            return False

        print(f"\n=== Handle Click Debug ===")
        print(f"Current state: {self.game.state}")

        if (
            hasattr(self.game, "auction_just_started")
            and self.game.auction_just_started
        ):
            print("Auction just started - ignoring click to prevent state transition")
            self.game.auction_just_started = False
            return False

        if self.game.state == "ROLL":
            if (
                not self.game.current_player_is_ai
                and self.game.game_mode == "abridged"
                and self.game.time_limit
                and self.game.pause_button.collidepoint(pos)
            ):
                current_time = pygame.time.get_ticks()

                if self.game.game_paused:
                    pause_duration = current_time - self.game.pause_start_time
                    self.game.total_pause_time += pause_duration
                    self.game.game_paused = False
                    self.game.board.add_message("Game resumed")
                else:
                    self.game.game_paused = True
                    self.game.pause_start_time = current_time
                    self.game.board.add_message("Game paused")

                return False

            if (
                not self.game.current_player_is_ai
                and self.game.roll_button.collidepoint(pos)
            ):
                if (
                    self.game.game_mode == "abridged"
                    and self.game.time_limit
                    and self.game.game_paused
                ):
                    self.game.board.add_message(
                        "Game is paused. Click Continue to resume."
                    )
                    return False
                else:
                    return self.game_actions.play_turn()

            human_players_remaining = any(
                not p.is_ai and not p.voluntary_exit and not p.bankrupt
                for p in self.game.players
            )

            if (
                not self.game.current_player_is_ai
                and human_players_remaining
                and self.game.quit_button.collidepoint(pos)
            ):
                confirm_exit = self.game_actions.show_exit_confirmation()

                if confirm_exit:
                    current_player = self.game.logic.players[
                        self.game.logic.current_player_index
                    ]

                    final_assets = self.game_actions.calculate_player_assets(
                        current_player
                    )

                    result = self.game_actions.handle_voluntary_exit(
                        current_player["name"], final_assets
                    )

                    if isinstance(result, dict):
                        return result
                    elif result:
                        self.game.board.add_message(
                            f"{current_player['name']} has voluntarily exited the game"
                        )

                        game_over_result = self.game_actions.check_game_over()
                        if game_over_result:
                            return game_over_result
                        if len(self.game.logic.players) > 0:
                            self.game.state = "ROLL"
                            self.game_actions.check_and_trigger_ai_turn()
                        else:
                            return self.game_actions.check_game_over()
                return False

        elif self.game.state == "BUY" and self.game.current_property is not None:
            current_player = self.game.logic.players[
                self.game.logic.current_player_index
            ]
            if current_player.get("in_jail", False):
                self.game.board.add_message(
                    f"{current_player['name']} cannot buy property while in jail!"
                )
                self.game.state = "ROLL"
                self.game.renderer.draw()
                pygame.display.flip()
                return False

            if self.game.yes_button.collidepoint(pos):
                self.game_actions.handle_buy_decision(True)
                self.game.dev_manager.deactivate()
                self.game.renderer.draw()
                pygame.display.flip()
                return False
            elif self.game.no_button.collidepoint(pos):
                self.game_actions.handle_buy_decision(False)
                self.game.dev_manager.deactivate()
                self.game.renderer.draw()
                pygame.display.flip()
                return False
            return False

        elif self.game.state == "AUCTION":
            print("\n=== Handling Auction Click ===")
            auction_result = self.handle_auction_click(pos)
            print(f"Auction click result: {auction_result}")

            if auction_result == True and not hasattr(self.game, "auction_completed"):
                print("Auction completed - changing state to ROLL")
                self.game.state = "ROLL"
                self.game.current_property = None
                self.game.board.update_ownership(self.game.logic.properties)
                self.game.update_current_player()
                self.game.dev_manager.deactivate()
                self.game_actions.check_and_trigger_ai_turn()
            else:
                print(
                    "Auction continues or completion in progress - maintaining AUCTION state"
                )
            return False

        print(f"Final state after click: {self.game.state}")
        return False

    def handle_motion(self, pos):
        if self.game.game_over:
            return False

        for emotion_ui in self.game.emotion_uis.values():
            emotion_ui.check_hover(pos)

        if self.game.state == "ROLL":
            hover_buttons = [
                self.game.roll_button.collidepoint(pos),
                self.game.quit_button.collidepoint(pos),
            ]

            if self.game.game_mode == "abridged" and self.game.time_limit:
                hover_buttons.append(self.game.pause_button.collidepoint(pos))

            return any(hover_buttons)
        elif self.game.state == "BUY":
            return self.game.yes_button.collidepoint(
                pos
            ) or self.game.no_button.collidepoint(pos)
        elif self.game.state == "AUCTION":
            return any(
                btn.collidepoint(pos) for btn in self.game.auction_buttons.values()
            )
        return False

    def handle_key(self, event):
        if self.game.dev_manager.is_active:
            if (
                hasattr(self.game.dev_manager, "notification")
                and self.game.dev_manager.notification
            ):
                if self.game.dev_manager.notification.handle_key(event):
                    self.game.dev_manager.deactivate()
                    return False
            return self.game.dev_manager.handle_key(event)

        if self.game.show_popup:
            if event.key in [pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE]:
                self.game.show_popup = False
                return False

        if self.game.show_card:
            if event.key in [pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE]:
                self.game.show_card = False
                self.game.current_card = None
                self.game.current_card_player = None
                return False

        any_player_moving = any(player.is_moving for player in self.game.players)
        if any_player_moving and event.key not in [
            pygame.K_LEFT,
            pygame.K_RIGHT,
            pygame.K_UP,
            pygame.K_DOWN,
        ]:
            print("Animations in progress, ignoring key input")
            return False

        print(f"\n=== Key Press Debug ===")
        print(f"Key: {pygame.key.name(event.key)}")
        print(f"Current state: {self.game.state}")

        if self.game.state == "ROLL":
            if not self.game.current_player_is_ai:
                if event.key in KEY_ROLL:
                    if (
                        self.game.game_mode == "abridged"
                        and self.game.time_limit
                        and self.game.game_paused
                    ):
                        self.game.board.add_message(
                            "Game is paused. Press P to resume."
                        )
                        return False
                    return self.game_actions.play_turn()
                elif event.key == pygame.K_q:
                    confirm_exit = self.game_actions.show_exit_confirmation()
                    if confirm_exit:
                        current_player = self.game.logic.players[
                            self.game.logic.current_player_index
                        ]
                        final_assets = self.game_actions.calculate_player_assets(
                            current_player
                        )
                        result = self.game_actions.handle_voluntary_exit(
                            current_player["name"], final_assets
                        )
                        if result:
                            self.game.board.add_message(
                                f"{current_player['name']} has voluntarily exited the game"
                            )
                            if len(self.game.logic.players) > 0:
                                self.game.state = "ROLL"
                                self.game_actions.check_and_trigger_ai_turn()
                            else:
                                return self.game_actions.check_game_over()
                    return False
                elif event.key == pygame.K_t and self.game.game_mode == "abridged":
                    self.game_actions.show_time_stats()
                elif (
                    event.key == pygame.K_p
                    and self.game.game_mode == "abridged"
                    and self.game.time_limit
                ):
                    current_time = pygame.time.get_ticks()
                    if self.game.game_paused:
                        pause_duration = current_time - self.game.pause_start_time
                        self.game.total_pause_time += pause_duration
                        self.game.game_paused = False
                        self.game.board.add_message("Game resumed")
                    else:
                        self.game.game_paused = True
                        self.game.pause_start_time = current_time
                        self.game.board.add_message("Game paused")
                    return False

        elif self.game.state == "BUY":
            if event.key in KEY_BUY:
                self.game_actions.handle_buy_decision(True)
                return False
            elif event.key in KEY_PASS:
                self.game_actions.handle_buy_decision(False)
                return False

        elif self.game.state == "AUCTION":
            print("Processing auction input")
            self.handle_auction_input(event)
            return False

        if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
            dx, dy = 0, 0
            if event.key == pygame.K_LEFT:
                dx = 10
            elif event.key == pygame.K_RIGHT:
                dx = -10
            elif event.key == pygame.K_UP:
                dy = 10
            elif event.key == pygame.K_DOWN:
                dy = -10
            self.game.board.update_offset(dx, dy)

        self.game.board.camera.handle_camera_controls(pygame.key.get_pressed())
        return None

    def handle_auction_input(self, event):
        if (
            not hasattr(self.game.logic, "current_auction")
            or self.game.logic.current_auction is None
        ):
            print("No active auction in handle_auction_input")
            return

        if self.game.show_card:
            print("Card is showing - ignoring auction input")
            return

        auction_data = self.game.logic.current_auction
        if "active_players" not in auction_data or not auction_data["active_players"]:
            print("No active players in auction - ignoring auction input")
            return

        if auction_data.get("completed", False):
            print("Auction is already completed - ignoring auction input")
            return

        if auction_data["current_bidder_index"] >= len(auction_data["active_players"]):
            print(
                f"Invalid current_bidder_index: {auction_data['current_bidder_index']} (active players: {len(auction_data['active_players'])})"
            )
            return

        current_bidder = auction_data["active_players"][
            auction_data["current_bidder_index"]
        ]
        current_bidder_obj = next(
            (p for p in self.game.players if p.name == current_bidder["name"]), None
        )

        print(f"Processing auction input for {current_bidder['name']}")

        if current_bidder.get("in_jail", False):
            self.game.board.add_message(
                f"{current_bidder['name']} cannot bid while in jail!"
            )
            auction_data["passed_players"].add(current_bidder["name"])
            self.game.logic.move_to_next_bidder()
            return

        if current_bidder_obj and not current_bidder_obj.is_ai:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.game.auction_bid_amount = self.game.auction_bid_amount[:-1]
                    print(
                        f"Backspace pressed - new bid amount: {self.game.auction_bid_amount}"
                    )

                elif event.key in [
                    pygame.K_0,
                    pygame.K_1,
                    pygame.K_2,
                    pygame.K_3,
                    pygame.K_4,
                    pygame.K_5,
                    pygame.K_6,
                    pygame.K_7,
                    pygame.K_8,
                    pygame.K_9,
                ]:
                    if len(self.game.auction_bid_amount) < 6:
                        self.game.auction_bid_amount += event.unicode
                        print(
                            f"Number key pressed - new bid amount: {self.game.auction_bid_amount}"
                        )

                elif event.key == pygame.K_RETURN:
                    print(
                        f"Enter key pressed - submitting bid: {self.game.auction_bid_amount}"
                    )
                    self._process_auction_bid(current_bidder)

                elif event.key == pygame.K_ESCAPE:
                    print(f"Escape key pressed - passing")
                    success, message = self.game.logic.process_auction_pass(
                        current_bidder
                    )
                    if message:
                        self.game.board.add_message(message)
                    if success:
                        print(f"{current_bidder['name']} passed successfully")
                    else:
                        print(f"Pass failed: {message}")

    def _process_auction_bid(self, current_bidder):
        try:
            bid_amount = int(self.game.auction_bid_amount or "0")
            success, message = self.game.logic.process_auction_bid(
                current_bidder, bid_amount
            )
            if message:
                self.game.board.add_message(message)
            if success:
                self.game.auction_bid_amount = ""
                print(f"Bid successful: £{bid_amount}")
            else:
                print(f"Bid failed: {message}")
        except ValueError:
            self.game.board.add_message("Please enter a valid number!")
            print("Invalid bid amount")

    def handle_auction_click(self, pos):
        print("\n=== Auction Click Debug ===")

        if (
            not hasattr(self.game.logic, "current_auction")
            or self.game.logic.current_auction is None
        ):
            print("Error: No active auction")
            self.game.state = "ROLL"
            return True

        if self.game.show_card:
            print("Card is showing - ignoring auction click")
            return False

        auction_data = self.game.logic.current_auction

        if auction_data is None:
            print("Error: Auction data is None in handle_auction_click")
            self.game.state = "ROLL"
            return True

        if "active_players" not in auction_data or not auction_data["active_players"]:
            print("No active players in auction")
            self.game.state = "ROLL"
            return True

        if auction_data.get("completed", False):
            print("Auction is already marked as completed - changing state to ROLL")
            self.game.state = "ROLL"
            return True

        current_bidder = auction_data["active_players"][
            auction_data["current_bidder_index"]
        ]

        if current_bidder.get("exited", False):
            print(f"Current bidder {current_bidder['name']} has exited - skipping")
            auction_data["passed_players"].add(current_bidder["name"])
            self.game.logic.move_to_next_bidder()
            return False

        current_bidder_obj = next(
            (p for p in self.game.players if p.name == current_bidder["name"]), None
        )

        if not current_bidder_obj or (
            hasattr(current_bidder_obj, "voluntary_exit")
            and current_bidder_obj.voluntary_exit
        ):
            print(
                f"Current bidder {current_bidder['name']} doesn't have UI representation or has voluntarily exited"
            )
            auction_data["passed_players"].add(current_bidder["name"])
            self.game.logic.move_to_next_bidder()
            return False

        if current_bidder.get("in_jail", False) and current_bidder.get("is_ai", False):
            print(f"AI bidder {current_bidder['name']} is in jail - auto-passing")
            auction_data["passed_players"].add(current_bidder["name"])
            self.game.logic.move_to_next_bidder()
            return False

        print(f"Current bidder: {current_bidder['name']}")
        print(f"Is AI: {current_bidder_obj.is_ai if current_bidder_obj else 'Unknown'}")
        print(f"Current bid amount input: {self.game.auction_bid_amount}")

        print(f"Bid button rect: {self.game.auction_buttons['bid']}")
        print(f"Pass button rect: {self.game.auction_buttons['pass']}")
        print(f"Click position: {pos}")
        print(
            f"Bid button collision: {self.game.auction_buttons['bid'].collidepoint(pos)}"
        )
        print(
            f"Pass button collision: {self.game.auction_buttons['pass'].collidepoint(pos)}"
        )

        if not current_bidder_obj or current_bidder_obj.is_ai:
            print("Current bidder is AI or not found - ignoring click")
            return False

        if self.game.auction_buttons["bid"].collidepoint(pos):
            print(f"Bid button clicked by {current_bidder['name']}")
            try:
                bid_amount = int(self.game.auction_bid_amount or "0")
                success, message = self.game.logic.process_auction_bid(
                    current_bidder, bid_amount
                )
                if message:
                    self.game.board.add_message(message)
                if success:
                    self.game.auction_bid_amount = ""
                    print(f"Bid successful: £{bid_amount}")
                else:
                    print(f"Bid failed: {message}")
            except ValueError:
                self.game.board.add_message("Please enter a valid number!")
                print("Invalid bid amount")

        elif self.game.auction_buttons["pass"].collidepoint(pos):
            print(f"Pass button clicked by {current_bidder['name']}")
            success, message = self.game.logic.process_auction_pass(current_bidder)
            if message:
                self.game.board.add_message(message)
            if success:
                print(f"{current_bidder['name']} passed successfully")
            else:
                print("Pass failed: {message}")

        result_message = self.game.logic.check_auction_end()
        print(f"Auction end check result: {result_message}")

        if result_message == "auction_completed":
            print("Auction is completed - showing results before changing state")

            if (
                hasattr(self.game.logic, "current_auction")
                and self.game.logic.current_auction
            ):
                auction_data = self.game.logic.current_auction
                if auction_data and auction_data.get("highest_bidder"):
                    winner = auction_data["highest_bidder"]
                    property_name = auction_data["property"]["name"]
                    bid_amount = auction_data["current_bid"]
                    self.game.board.add_message(
                        f"{winner['name']} won {property_name} for £{bid_amount}"
                    )
                else:
                    property_name = auction_data["property"]["name"]
                    self.game.board.add_message(f"No one bid on {property_name}")

            self.game.auction_end_time = pygame.time.get_ticks()
            self.game.auction_end_delay = 3000
            self.game.auction_completed = True

            self.game.board.update_ownership(self.game.logic.properties)
            return False

        print("Auction continues - returning False")
        return False
