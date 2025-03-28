# Property Tycoon main.py
# Created for 2025 UOS Year 2 G6046: Software Engineering Project-Group 5
# -*- coding: utf-8 -*-
# It contains the main function for the game.

import pygame
import sys
import asyncio
import os
import random
import logging
from datetime import datetime


logs_dir = "logs"
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

log_filename = os.path.join(
    logs_dir, f"game_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(log_filename, mode="w", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)


class LogRedirector:
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level
        self.buffer = ""

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            if line.strip():
                self.logger.log(self.level, line.rstrip())
        sys.__stdout__.write(buf)

    def flush(self):
        pass


sys.stdout = LogRedirector(logger, logging.INFO)
sys.stderr = LogRedirector(logger, logging.ERROR)

logger.info("=== Game Session Started ===")

file_handler.flush()

pygame.init()
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from src.Board import Board
from src.Game import Game
from src.Player import Player
from src.GameRenderer import GameRenderer
from src.GameEventHandler import GameEventHandler
from src.GameActions import GameActions
from src.Sound_Manager import sound_manager
from src.UI import (
    MainMenuPage,
    StartPage,
    GameModePage,
    EndGamePage,
    SettingsPage,
    HowToPlayPage,
    AIDifficultyPage,
    CreditsPage,
    KeyboardShortcutsPage,
)
from src.Font_Manager import font_manager

WINDOW_SIZE = (1280, 720)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255)

STARTING_BANK_MONEY = 50000
STARTING_PLAYER_MONEY = 1500
JAIL_FINE = 50
PASSING_GO_AMOUNT = 200
HOTEL_VALUE_IN_HOUSES = 5  # A hotel is worth 5 houses
HOTEL_REPLACES_HOUSES = True  # When building a hotel, houses are returned to bank

FPS = 30

GAME_INSTRUCTIONS = [
    "Use WASD or Arrow keys to move",
    "Press + or - to zoom",
    "Press ESC to exit game",
    "Use mouse to click buttons",
    "Buy properties when landing on them",
    "You must complete one lap around the board before buying properties",
    "Build houses/hotels on owned property sets",
    "Pay rent when landing on others' properties",
    "Collect £200 when passing GO",
]


async def apply_screen_settings(resolution):
    global WINDOW_SIZE
    WINDOW_SIZE = resolution
    screen = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)

    pygame.display.set_caption("Property Tycoon Alpha 25.03.2025")
    try:
        icon_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "assets", "image", "icon.ico"
        )
        icon = pygame.image.load(icon_path)
        pygame.display.set_icon(icon)
    except (pygame.error, FileNotFoundError) as e:
        logger.error(f"Could not load game icon: {e}")

    font_manager.update_scale_factor(resolution[0], resolution[1])

    if pygame.display.get_surface():
        current_w, current_h = pygame.display.get_surface().get_size()
        if current_w != resolution[0] or current_h != resolution[1]:
            screen = pygame.display.set_mode(resolution, pygame.RESIZABLE)
            pygame.display.flip()

    return screen


def can_develop(self, player):
    return self.dev_manager.can_develop(player)


def create_game(player_info, game_settings):
    if not player_info or not game_settings:
        raise ValueError("Missing player info or game settings")

    total_players, player_names, ai_count, token_indices = player_info
    if not isinstance(total_players, int) or not isinstance(ai_count, int):
        raise ValueError("Invalid player counts")

    players = []
    player_number = 1

    bank_money = STARTING_BANK_MONEY

    for i, name in enumerate(player_names[: total_players - ai_count]):
        if not name.strip():
            continue
        token_index = token_indices[i] + 1
        player = Player(name, player_number=token_index)
        player.money = STARTING_PLAYER_MONEY
        bank_money -= STARTING_PLAYER_MONEY
        players.append(player)
        player_number += 1

    for i, name in enumerate(player_names[total_players - ai_count :]):
        if not name.strip():
            continue
        token_index = token_indices[total_players - ai_count + i] + 1
        player = Player(
            name,
            is_ai=True,
            player_number=token_index,
            ai_difficulty=game_settings.get("ai_difficulty", "easy"),
        )
        player.money = STARTING_PLAYER_MONEY
        bank_money -= STARTING_PLAYER_MONEY
        players.append(player)
        player_number += 1

    if not players:
        raise ValueError("No valid players created")

    game = Game(
        players,
        game_mode=game_settings.get("mode", "full"),
        time_limit=game_settings.get("time_limit"),
        ai_difficulty=game_settings.get("ai_difficulty", "easy"),
    )

    game.bank_money = bank_money
    game.free_parking_pot = 0

    sound_manager.play_sound("game_start")

    return game


async def run_game(game, game_settings):
    running = True
    game_over_data = None
    last_time_check = pygame.time.get_ticks()
    last_ai_progress_time = pygame.time.get_ticks()
    ai_timeout_duration = 10000

    last_log_flush_time = pygame.time.get_ticks()
    log_flush_interval = 1500

    logger.info(f"Starting game with settings: {game_settings}")
    logger.info(f"Players: {[player.name for player in game.players]}")
    logger.info(f"Game mode: {game_settings.get('mode', 'full')}")
    if game_settings.get("time_limit"):
        logger.info(f"Time limit: {game_settings.get('time_limit')} seconds")

    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            handler.flush()

    time_warning_active = False
    warning_flash_rate = 300
    warning_edge_size = 0
    warning_max_edge = 60
    last_warning_update = 0

    clock = pygame.time.Clock()

    game_actions = GameActions(game)
    renderer = GameRenderer(game, game_actions)
    game.renderer = renderer
    event_handler = GameEventHandler(game, game_actions)

    game.time_warning_start = 30
    game.warning_flash_rate = 200
    game.warning_border_max_width = 60

    event_handler.handle_motion((0, 0))

    sound_manager.play_music(loop=-1)

    while running:
        await asyncio.sleep(0)

        current_time = pygame.time.get_ticks()

        if current_time - last_log_flush_time > log_flush_interval:
            last_log_flush_time = current_time
            for handler in logger.handlers:
                if isinstance(handler, logging.FileHandler):
                    handler.flush()

        if (
            game_settings["mode"] == "abridged"
            and current_time - last_time_check > 1000
            and not game.game_paused
        ):
            last_time_check = current_time
            time_limit_result = game.check_time_limit()

            if game.time_limit and not game.game_paused:
                elapsed = (
                    current_time - game.start_time - game.total_pause_time
                ) // 1000
                remaining = max(0, game.time_limit - elapsed)

                if remaining <= 30 and not hasattr(game, "time_limit_reached"):
                    time_warning_active = True
                    game.time_warning_active = True

                    if current_time - last_warning_update > 50:
                        last_warning_update = current_time
                        warning_intensity = (30 - remaining) / 30
                        warning_edge_target = int(warning_max_edge * warning_intensity)
                        warning_edge_size = min(
                            warning_edge_size + 2, warning_edge_target
                        )
                        game.warning_border_width = warning_edge_size
                else:
                    time_warning_active = False
                    game.time_warning_active = False
                    warning_edge_size = max(0, warning_edge_size - 2)
                    game.warning_border_width = warning_edge_size

            if time_limit_result:
                logger.info(
                    "Time limit reached and all players completed same number of laps - ending game"
                )
                if isinstance(time_limit_result, dict):
                    game_over_data = time_limit_result
                else:
                    game_over_data = game_actions.end_abridged_game()
                running = False
                continue

        if game.current_player_is_ai and not game.game_paused:
            if current_time - last_ai_progress_time > ai_timeout_duration:
                logger.warning(
                    f"AI player turn timeout reached after {ai_timeout_duration/1000} seconds"
                )

                if game.logic.players and len(game.logic.players) > 0:
                    current_player = game.logic.players[game.logic.current_player_index]
                    logger.warning(
                        f"Forcing AI player {current_player['name']} to skip their turn due to timeout"
                    )

                    if game.state == "DEVELOPMENT":
                        game.state = "ROLL"
                        game.selected_property = None
                        game.development_mode = False
                        logger.info("Closing stuck development UI due to timeout")

                    game.logic.current_player_index = (
                        game.logic.current_player_index + 1
                    ) % len(game.logic.players)

                    game.state = "ROLL"
                    game.current_player_is_ai = False

                    game_actions.check_and_trigger_ai_turn()

                last_ai_progress_time = current_time

        if not game.current_player_is_ai:
            last_ai_progress_time = current_time

        renderer.draw()

        if hasattr(game, "waiting_for_animation") and game.waiting_for_animation:
            any_moving = any(player.is_moving for player in game.players)
            if not any_moving:
                game.waiting_for_animation = False
            else:
                pygame.display.flip()
                continue

        for game_event in pygame.event.get():
            if game_event.type == pygame.QUIT:
                safe_exit()
            elif game_event.type == pygame.MOUSEBUTTONDOWN:
                any_moving = any(player.is_moving for player in game.players)
                if any_moving and game.state == "AUCTION":
                    logger.info(
                        "Animations in progress during AUCTION state - delaying click processing"
                    )
                    pygame.display.flip()
                    continue

                game_over_data = event_handler.handle_click(game_event.pos)
                if game_over_data:
                    running = False

                sound_manager.play_sound("menu_click")
            elif game_event.type == pygame.KEYDOWN:
                logger.debug(f"Key pressed: {pygame.key.name(game_event.key)}")

                if game_event.key == pygame.K_ESCAPE:
                    if game.game_mode == "abridged" and game.time_limit:
                        current_time = pygame.time.get_ticks()
                        if game.game_paused:
                            pause_duration = current_time - game.pause_start_time
                            game.total_pause_time += pause_duration
                            game.game_paused = False
                            game.board.add_message("Game resumed")
                        else:
                            game.game_paused = True
                            game.pause_start_time = current_time
                            game.board.add_message("Game paused")
                    pass
                elif game.state == "AUCTION":
                    logger.info("Handling auction key input in main loop")
                    event_handler.handle_auction_input(game_event)
                else:
                    game_over_data = event_handler.handle_key(game_event)
                    if game_over_data:
                        running = False
            elif game_event.type == pygame.VIDEORESIZE:
                await apply_screen_settings((game_event.w, game_event.h))
            elif game_event.type == pygame.MOUSEMOTION:
                event_handler.handle_motion(game_event.pos)

        current_time = pygame.time.get_ticks()
        if (
            hasattr(game, "last_debug_time")
            and current_time - game.last_debug_time < 1000
        ):
            pass
        else:
            if hasattr(game, "state"):
                logger.debug(f"Current game state: {game.state}")
                game.last_debug_time = current_time

                if game.state == "AUCTION" and hasattr(game.logic, "current_auction"):
                    auction_data = game.logic.current_auction
                    if auction_data is not None:
                        logger.debug(f"\n=== Auction State Debug ===")
                        logger.debug(f"Property: {auction_data['property']['name']}")
                        logger.debug(f"Current bid: £{auction_data['current_bid']}")
                        logger.debug(f"Minimum bid: £{auction_data['minimum_bid']}")

                        if auction_data["highest_bidder"]:
                            logger.debug(
                                f"Highest bidder: {auction_data['highest_bidder']['name']}"
                            )
                        else:
                            logger.debug("No bids yet")

                        logger.debug(
                            f"Current bidder index: {auction_data['current_bidder_index']}"
                        )
                        if auction_data["active_players"]:
                            current_bidder = auction_data["active_players"][
                                auction_data["current_bidder_index"]
                            ]
                            logger.debug(f"Current bidder: {current_bidder['name']}")

                        logger.debug(
                            f"Passed players: {auction_data.get('passed_players', set())}"
                        )
                        logger.debug(
                            f"Active players: {[p['name'] for p in auction_data.get('active_players', [])]}"
                        )
                        logger.debug(
                            f"Completed: {auction_data.get('completed', False)}"
                        )
                    else:
                        logger.debug("\n=== Auction State Debug ===")
                        logger.debug("No auction data available")

        if (
            hasattr(game.logic, "current_auction")
            and game.logic.current_auction
            and not game.logic.current_auction.get("completed", False)
        ):
            if game.state != "AUCTION":
                logger.warning(
                    "Auction in progress but state is not AUCTION - correcting state"
                )
                game.state = "AUCTION"

        if (
            game.state == "ROLL"
            and game.logic.players
            and not any(player.is_moving for player in game.players)
        ):
            current_player = game.logic.players[game.logic.current_player_index]

            ai_player = None
            for player in game.players:
                if player.name == current_player["name"]:
                    ai_player = player
                    break

            if ai_player and ai_player.is_ai:
                if not isinstance(ai_player.position, int) or not (
                    1 <= ai_player.position <= 40
                ):
                    logger.warning(
                        f"Warning: Invalid position {ai_player.position} detected for AI {ai_player.name}, resetting to position 1"
                    )
                    ai_player.position = 1
                    current_player["position"] = 1

                game_over_data = game_actions.handle_ai_turn(current_player)
                if game_over_data:
                    running = False

        if (
            game.state == "AUCTION"
            and hasattr(game.logic, "current_auction")
            and not any(player.is_moving for player in game.players)
        ):
            auction_data = game.logic.current_auction

            if (
                auction_data is not None
                and not auction_data.get("completed", False)
                and auction_data.get("active_players")
                and not hasattr(game, "auction_processing")
            ):
                game.auction_processing = True
                current_bidder_index = auction_data["current_bidder_index"]

                if current_bidder_index < len(auction_data["active_players"]):
                    current_bidder = auction_data["active_players"][
                        current_bidder_index
                    ]

                    bidder_obj = None
                    for player in game.players:
                        if player.name == current_bidder["name"]:
                            bidder_obj = player
                            break

                    if (
                        bidder_obj
                        and bidder_obj.is_ai
                        and current_bidder["name"]
                        not in auction_data.get("passed_players", set())
                    ):
                        logger.debug(f"\n=== AI Auction Turn in Main Loop ===")
                        logger.debug(f"AI Player: {current_bidder['name']}")
                        logger.debug(f"Current bid: £{auction_data['current_bid']}")
                        logger.debug(f"Minimum bid: £{auction_data['minimum_bid']}")
                        logger.debug(f"AI money: £{current_bidder['money']}")

                        ai_decision = random.random() > 0.5
                        if (
                            ai_decision
                            and current_bidder["money"] >= auction_data["minimum_bid"]
                        ):
                            bid_amount = min(
                                current_bidder["money"],
                                auction_data["minimum_bid"] + random.randint(10, 50),
                            )
                            logger.debug(
                                f"AI {current_bidder['name']} bids £{bid_amount}"
                            )
                            success, message = game.logic.process_auction_bid(
                                current_bidder, bid_amount
                            )
                            game.board.add_message(message)
                        else:
                            logger.debug(f"AI {current_bidder['name']} passes")
                            success, message = game.logic.process_auction_pass(
                                current_bidder
                            )
                            game.board.add_message(message)

                if (
                    hasattr(game.logic, "current_auction")
                    and game.logic.current_auction
                ):
                    result_message = game.logic.check_auction_end()
                    if result_message == "auction_completed":
                        logger.info("Auction completed in main loop - setting up delay")

                        if (
                            hasattr(game.logic, "current_auction")
                            and game.logic.current_auction is not None
                        ):
                            if game.logic.current_auction.get("highest_bidder"):
                                winner = game.logic.current_auction["highest_bidder"]
                                property_name = game.logic.current_auction["property"][
                                    "name"
                                ]
                                bid_amount = game.logic.current_auction["current_bid"]
                                game.board.add_message(
                                    f"{winner['name']} won {property_name} for £{bid_amount}"
                                )
                            else:
                                property_name = game.logic.current_auction["property"][
                                    "name"
                                ]
                                game.board.add_message(f"No one bid on {property_name}")

                        game.auction_end_time = pygame.time.get_ticks()
                        game.auction_end_delay = 3000
                        game.auction_completed = True
                        game.board.update_ownership(game.logic.properties)

                delattr(game, "auction_processing")

        any_moving = any(player.is_moving for player in game.players)
        if (
            not any_moving
            and game.state == "AUCTION"
            and hasattr(game.logic, "current_auction")
            and game.logic.current_auction
            and game.logic.current_auction.get("completed", False)
        ):
            logger.warning(
                "Auction marked as completed but state not updated - forcing state to ROLL"
            )
            game.state = "ROLL"
            game.board.update_ownership(game.logic.properties)

        if (
            not any_moving
            and game.state == "AUCTION"
            and (
                not hasattr(game.logic, "current_auction")
                or game.logic.current_auction is None
            )
        ):
            logger.warning(
                "State is AUCTION but no auction data exists - resetting to ROLL"
            )
            game.state = "ROLL"

        if (
            game_settings["mode"] == "full"
            and game_actions.check_one_player_remains()
            and not game_over_data
        ):
            logger.info("Only one player remains - ending game")
            game_over_data = game_actions.end_full_game()
            running = False

        elif (
            game_settings["mode"] == "abridged"
            and game_actions.check_one_player_remains()
            and not game_over_data
        ):
            logger.info("Only one player remains in abridged mode - ending game")
            game_over_data = game_actions.end_abridged_game()
            running = False

        pygame.display.flip()

        clock.tick(FPS)

    sound_manager.stop_music()
    return game_over_data


async def handle_end_game(game_over_data):
    logger.info("Entering handle_end_game function")
    logger.debug(f"Game over data: {game_over_data}")

    sound_manager.play_sound("game_over")

    pygame.display.flip()

    clock = pygame.time.Clock()

    if isinstance(game_over_data, bool):
        logger.warning("WARNING: Game over data is a boolean instead of a dictionary")
        game_over_data = {
            "winner": "Last Player Standing",
            "final_assets": {},
            "bankrupted_players": [],
            "voluntary_exits": [],
            "tied_winners": [],
            "lap_count": {},
        }

    end_page = EndGamePage(
        winner_name=game_over_data["winner"],
        final_assets=game_over_data.get("final_assets", {}),
        bankrupted_players=game_over_data.get("bankrupted_players", []),
        voluntary_exits=game_over_data.get("voluntary_exits", []),
        tied_winners=game_over_data.get("tied_winners", []),
        lap_count=game_over_data.get("lap_count", {}),
    )

    logger.info("EndGamePage created successfully")

    debug_drawn = False
    current_page = end_page

    while True:
        await asyncio.sleep(0)
        current_page.draw()
        pygame.display.flip()

        clock.tick(FPS)

        if not debug_drawn and isinstance(current_page, EndGamePage):
            logger.debug("EndGamePage drawn")
            debug_drawn = True

        for end_event in pygame.event.get():
            if end_event.type == pygame.QUIT:
                safe_exit()
            elif end_event.type == pygame.MOUSEBUTTONDOWN:
                result = current_page.handle_click(end_event.pos)

                if isinstance(current_page, EndGamePage):
                    if result == "play_again":
                        return True
                    elif result == "quit":
                        safe_exit()
                    elif result == "credits":
                        current_page = CreditsPage()
                elif isinstance(current_page, CreditsPage) and result:
                    current_page = end_page
            elif end_event.type == pygame.KEYDOWN:
                result = current_page.handle_key(end_event)

                if isinstance(current_page, EndGamePage):
                    if result == "play_again":
                        return True
                    elif result == "quit":
                        safe_exit()
                    elif result == "credits":
                        current_page = CreditsPage()
            elif end_event.type == pygame.MOUSEMOTION:
                current_page.handle_motion(end_event.pos)


async def show_logo_screen(screen, logo_path, scale_factor=0.5):
    try:
        base_path = os.path.dirname(os.path.abspath(__file__))
        bg_path = os.path.join(base_path, "assets/image/starterbackground.png")
        original_background = pygame.image.load(bg_path)
        window_size = screen.get_size()
        window_width, window_height = window_size

        bg_width, bg_height = original_background.get_size()
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

        background = pygame.transform.scale(
            original_background, (scaled_width, scaled_height)
        )

        logo = pygame.image.load(logo_path)

        logo_width = int(window_size[0] * scale_factor)
        logo_height = int(logo_width * (logo.get_height() / logo.get_width()))
        logo = pygame.transform.scale(logo, (logo_width, logo_height))

        x = (window_size[0] - logo_width) // 2
        y = (window_size[1] - logo_height) // 2

        # Fade in
        for alpha in range(0, 255, 5):
            screen.fill((0, 0, 0))
            screen.blit(background, (pos_x, pos_y))

            overlay = pygame.Surface(window_size, pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            screen.blit(overlay, (0, 0))

            logo_surface = pygame.Surface((logo_width, logo_height), pygame.SRCALPHA)
            logo_surface.fill((255, 255, 255, 0))
            logo_surface.blit(logo, (0, 0))
            logo_surface.set_alpha(alpha)
            screen.blit(logo_surface, (x, y))

            pygame.display.flip()
            await asyncio.sleep(0.01)

        await asyncio.sleep(1.5)

        for alpha in range(255, -1, -5):
            screen.fill((0, 0, 0))
            screen.blit(background, (pos_x, pos_y))

            overlay = pygame.Surface(window_size, pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            screen.blit(overlay, (0, 0))

            logo_surface = pygame.Surface((logo_width, logo_height), pygame.SRCALPHA)
            logo_surface.fill((255, 255, 255, 0))
            logo_surface.blit(logo, (0, 0))
            logo_surface.set_alpha(alpha)
            screen.blit(logo_surface, (x, y))

            pygame.display.flip()
            await asyncio.sleep(0.01)

    except Exception as e:
        logger.error(f"Error showing logo screen: {e}")


async def show_company_logo(screen):
    base_path = os.path.dirname(os.path.abspath(__file__))
    from src.Sound_Manager import sound_manager

    logo_path = os.path.join(base_path, "assets/image/Watson Games 2025.png")
    sound_manager.play_sound("watson_games")
    await show_logo_screen(screen, logo_path, scale_factor=0.7)

    group_logo_path = os.path.join(base_path, "assets/image/Group 5 Persent.png")
    sound_manager.play_sound("group_present")
    await show_logo_screen(screen, group_logo_path, scale_factor=0.9)

    sound_manager.play_sound("game_start")


async def main():
    global WINDOW_SIZE
    font_manager.update_scale_factor(WINDOW_SIZE[0], WINDOW_SIZE[1])
    screen = await apply_screen_settings(WINDOW_SIZE)

    sound_manager.load_sounds()
    sound_manager.load_music()

    await show_company_logo(screen)

    clock = pygame.time.Clock()

    while True:
        await asyncio.sleep(0)
        current_page = MainMenuPage(instructions=GAME_INSTRUCTIONS)
        player_info = None
        game_settings = None
        ai_difficulty = None

        game_running = True
        while game_running:
            current_page.draw()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    safe_exit()
                elif (
                    event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN
                ):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        sound_manager.play_sound("menu_click")
                    result = (
                        current_page.handle_click(event.pos)
                        if event.type == pygame.MOUSEBUTTONDOWN
                        else current_page.handle_key(event)
                    )

                    if result:
                        if isinstance(current_page, MainMenuPage):
                            if result == "start":
                                current_page = StartPage(instructions=GAME_INSTRUCTIONS)
                            elif result == "how_to_play":
                                current_page = HowToPlayPage(
                                    instructions=GAME_INSTRUCTIONS
                                )
                            elif result == "settings":
                                current_page = SettingsPage(
                                    instructions=GAME_INSTRUCTIONS
                                )
                        elif isinstance(current_page, HowToPlayPage):
                            if result == "keyboard_shortcuts":
                                current_page = KeyboardShortcutsPage(
                                    instructions=GAME_INSTRUCTIONS
                                )
                            else:
                                current_page = MainMenuPage(
                                    instructions=GAME_INSTRUCTIONS
                                )
                        elif isinstance(current_page, KeyboardShortcutsPage):
                            current_page = HowToPlayPage(instructions=GAME_INSTRUCTIONS)
                        elif isinstance(current_page, SettingsPage):
                            settings = current_page.get_settings()
                            if settings["resolution"] != WINDOW_SIZE:
                                screen = await apply_screen_settings(
                                    settings["resolution"]
                                )
                            current_page = MainMenuPage(instructions=GAME_INSTRUCTIONS)
                        elif isinstance(current_page, StartPage):
                            if result == "back":
                                current_page = MainMenuPage(
                                    instructions=GAME_INSTRUCTIONS
                                )
                            else:
                                player_info = current_page.get_player_info()
                                if player_info[2] > 0:
                                    current_page = AIDifficultyPage(
                                        instructions=GAME_INSTRUCTIONS
                                    )
                                else:
                                    current_page = GameModePage(
                                        instructions=GAME_INSTRUCTIONS
                                    )
                        elif isinstance(current_page, AIDifficultyPage):
                            if result == "back":
                                current_page = StartPage(instructions=GAME_INSTRUCTIONS)
                            else:
                                ai_difficulty = result
                                current_page = GameModePage(
                                    instructions=GAME_INSTRUCTIONS
                                )
                        elif isinstance(current_page, GameModePage):
                            if result == "back":
                                if ai_difficulty:
                                    current_page = AIDifficultyPage(
                                        instructions=GAME_INSTRUCTIONS
                                    )
                                else:
                                    current_page = StartPage(
                                        instructions=GAME_INSTRUCTIONS
                                    )
                            else:
                                game_settings = current_page.get_game_settings()
                                if ai_difficulty:
                                    game_settings["ai_difficulty"] = ai_difficulty

                                game = create_game(player_info, game_settings)
                                game_over_data = await run_game(game, game_settings)

                                if game_over_data:
                                    play_again = await handle_end_game(game_over_data)
                                    if play_again:
                                        current_page = MainMenuPage(
                                            instructions=GAME_INSTRUCTIONS
                                        )

                elif event.type == pygame.MOUSEMOTION:
                    current_page.handle_motion(event.pos)
                elif event.type == pygame.VIDEORESIZE:
                    screen = await apply_screen_settings((event.w, event.h))

            pygame.display.flip()

            # Limit fps
            clock.tick(FPS)


def safe_exit(code=0):
    logger.info("Game is shutting down...")

    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__

    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            handler.flush()

    logger.info("=== Game Session Ended ===")

    logging.shutdown()

    pygame.quit()
    sys.exit(code)


if __name__ == "__main__":
    asyncio.run(main())
