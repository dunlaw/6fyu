# Base on PropertyTycoonCardData.xlsx from canvas
# script based on Eric's provided flowchart photo (flowchart.drawio.png)
# will add more comment later to reference for which part of code is based on which part of the flowchart

import pygame
import random
from src.Loadexcel import load_property_data
from src.Ai_Player_Logic import EasyAIPlayer, HardAIPlayer

pot_luck_cards = [
    {
        "text": "You inherit £200",
        "action": lambda player, bank, free_parking: (
            player["money"] + 200,
            bank - 200,
            free_parking,
        ),
    },
    {
        "text": "You have won 2nd prize in a beauty contest, collect £50",
        "action": lambda player, bank, free_parking: (
            player["money"] + 50,
            bank - 50,
            free_parking,
        ),
    },
    {
        "text": "You are up the creek with no paddle - go back to the Old Creek",
        "action": lambda player, bank, free_parking: (2, bank, free_parking),
    },
    {
        "text": "Student loan refund. Collect £20",
        "action": lambda player, bank, free_parking: (
            player["money"] + 20,
            bank - 20,
            free_parking,
        ),
    },
    {
        "text": "Bank error in your favour. Collect £200",
        "action": lambda player, bank, free_parking: (
            player["money"] + 200,
            bank - 200,
            free_parking,
        ),
    },
    {
        "text": "Pay bill for text books of £100",
        "action": lambda player, bank, free_parking, board=None: board.handle_payment_to_bank(
            player, 100
        ),
    },
    {
        "text": "Mega late night taxi bill pay £50",
        "action": lambda player, bank, free_parking, board=None: board.handle_payment_to_bank(
            player, 50
        ),
    },
    {
        "text": "Advance to go",
        "action": lambda player, bank, free_parking: (1, bank, free_parking),
    },
    {
        "text": "From sale of Bitcoin you get £50",
        "action": lambda player, bank, free_parking: (
            player["money"] + 50,
            bank - 50,
            free_parking,
        ),
    },
    {
        "text": "Bitcoin assets fall - pay off Bitcoin short fall",
        "action": lambda player, bank, free_parking, board=None: board.handle_payment_to_bank(
            player, 50
        ),
    },
    {
        "text": "Pay a £10 fine or take opportunity knocks",
        "action": lambda player, bank, free_parking, board=None: board.handle_payment_to_bank(
            player, 10, True
        ),
    },
    {
        "text": "Pay insurance fee of £50",
        "action": lambda player, bank, free_parking, board=None: board.handle_payment_to_bank(
            player, 50, True
        ),
    },
    {
        "text": "Savings bond matures, collect £100",
        "action": lambda player, bank, free_parking: (
            player["money"] + 100,
            bank - 100,
            free_parking,
        ),
    },
    {
        "text": "Go to jail. Do not pass GO, do not collect £200",
        "action": lambda player, bank, free_parking: (11, bank, free_parking),
    },
    {
        "text": "Received interest on shares of £25",
        "action": lambda player, bank, free_parking: (
            player["money"] + 25,
            bank - 25,
            free_parking,
        ),
    },
    {
        "text": "It's your birthday. Collect £10 from each player",
        "action": lambda player, bank, free_parking, board=None: board.handle_birthday_collection(
            player
        ),
    },
    {
        "text": "Get out of jail free",
        "action": lambda player, bank, free_parking: (
            player["position"],
            bank,
            free_parking,
        ),
    },
]

opportunity_knocks_cards = [
    {
        "text": "Bank pays you divided of £50",
        "action": lambda player, bank, free_parking: (
            player["money"] + 50,
            bank - 50,
            free_parking,
        ),
    },
    {
        "text": "You have won a lip sync battle. Collect £100",
        "action": lambda player, bank, free_parking: (
            player["money"] + 100,
            bank - 100,
            free_parking,
        ),
    },
    {
        "text": "Advance to Turing Heights",
        "action": lambda player, bank, free_parking: (40, bank, free_parking),
    },
    {
        "text": "Advance to Han Xin Gardens",
        "action": lambda player, bank, free_parking: (
            25,
            bank + (200 if player["position"] > 25 else 0),
            free_parking,
        ),
    },
    {
        "text": "Fined £15 for speeding",
        "action": lambda player, bank, free_parking, board=None: board.handle_payment_to_bank(
            player, 15, True
        ),
    },
    {
        "text": "Pay university fees of £150",
        "action": lambda player, bank, free_parking, board=None: board.handle_payment_to_bank(
            player, 150
        ),
    },
    {
        "text": "Take a trip to Hove station",
        "action": lambda player, bank, free_parking: (
            16,
            bank + (200 if player["position"] > 16 else 0),
            free_parking,
        ),
    },
    {
        "text": "Loan matures, collect £150",
        "action": lambda player, bank, free_parking: (
            player["money"] + 150,
            bank - 150,
            free_parking,
        ),
    },
    {
        "text": "You are assessed for repairs, £40/house, £115/hotel",
        "action": lambda player, bank, free_parking, board=None: board.handle_repair_assessment(
            player, 40, 115
        ),
    },
    {
        "text": "Advance to GO",
        "action": lambda player, bank, free_parking: (1, bank, free_parking),
    },
    {
        "text": "You are assessed for repairs, £25/house, £100/hotel",
        "action": lambda player, bank, free_parking, board=None: board.handle_repair_assessment(
            player, 25, 100
        ),
    },
    {
        "text": "Go back 3 spaces",
        "action": lambda player, bank, free_parking: (
            ((player["position"] - 1 - 3) % 40) + 1,
            bank,
            free_parking,
        ),
    },
    {
        "text": "Advance to Skywalker Drive",
        "action": lambda player, bank, free_parking: (
            12,
            bank + (200 if player["position"] > 12 else 0),
            free_parking,
        ),
    },
    {
        "text": "Go to jail. Do not pass GO, do not collect £200",
        "action": lambda player, bank, free_parking: (11, bank, free_parking),
    },
    {
        "text": "Drunk in charge of a hoverboard. Fine £30",
        "action": lambda player, bank, free_parking, board=None: board.handle_payment_to_bank(
            player, 30, True
        ),
    },
    {
        "text": "Get out of jail free",
        "action": lambda player, bank, free_parking: (
            player["position"],
            bank,
            free_parking,
        ),
    },
]


class GameLogic:
    BANK_LIMIT = 50000
    MAX_HOUSES_PER_PROPERTY = 4
    MAX_HOTELS_PER_PROPERTY = 1
    GAME_TOKENS = ["boot", "smartphone", "ship", "hatstand", "cat", "iron"]

    def __init__(self):
        self.players = []
        self.bank_money = self.BANK_LIMIT
        self.free_parking_fund = 0
        self.current_player_index = 0
        self.properties = load_property_data()
        self.is_going_to_jail = False
        self.last_dice_roll = None
        self.doubles_count = 0
        self.message_queue = []
        self.bankrupted_players = []
        self.voluntary_exits = []
        self.jail_free_cards = {}
        self.completed_circuits = {}
        self.available_tokens = self.GAME_TOKENS.copy()
        self.pot_luck_cards = pot_luck_cards.copy()
        self.opportunity_knocks_cards = opportunity_knocks_cards.copy()
        random.shuffle(self.pot_luck_cards)
        random.shuffle(self.opportunity_knocks_cards)
        self.ai_difficulty = "easy"
        self.ai_player = EasyAIPlayer()
        self.game = None

    def validate_bank_transaction(self, amount):
        if amount > self.bank_money:
            raise ValueError("Bank does not have sufficient funds")
        return True

    def pay_from_bank(self, player, amount):
        if self.validate_bank_transaction(amount):
            self.bank_money -= amount
            player["money"] += amount
            return True
        return False

    def pay_to_bank(self, player, amount):
        if player["money"] >= amount:
            player["money"] -= amount
            self.bank_money += amount
            return True
        return False

    def game_start(self):
        self.properties = load_property_data()
        if self.properties is None:
            return False
        return True

    def add_player(self, player):
        if len(self.players) < 5:
            player_name = player.name if hasattr(player, "name") else player
            player_is_ai = (
                getattr(player, "is_ai", False) if hasattr(player, "is_ai") else False
            )

            token_index = (
                getattr(player, "player_number", 1)
                if hasattr(player, "player_number")
                else 1
            )
            token = self.GAME_TOKENS[
                min(token_index - 1, len(self.GAME_TOKENS) - 1) % len(self.GAME_TOKENS)
            ]

            new_player = {
                "name": player_name,
                "money": 1500,
                "position": 1,
                "is_ai": player_is_ai,
                "properties": [],
                "token": token,
            }
            self.players.append(new_player)
            self.completed_circuits[player_name] = 0
            return True, f"Added player {player_name} with {token} token"
        return False, "Maximum number of players reached"

    def advance_to_next_player(self):
        if not self.players:
            return

        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        current_player = self.players[self.current_player_index]

        while current_player.get("exited", False) or current_player.get(
            "bankrupt", False
        ):
            self.current_player_index = (self.current_player_index + 1) % len(
                self.players
            )
            current_player = self.players[self.current_player_index]

        return current_player

    def play_turn(self):
        if not self.players:
            return None, None

        current_player = self.players[self.current_player_index]
        while current_player.get("exited", False) or current_player.get(
            "bankrupt", False
        ):
            self.current_player_index = (self.current_player_index + 1) % len(
                self.players
            )
            current_player = self.players[self.current_player_index]

        self.is_going_to_jail = False

        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        self.last_dice_roll = (dice1, dice2)

        if current_player.get("in_jail", False):
            success, message = self.try_leave_jail(current_player, dice1, dice2)
            if not success:
                self.advance_to_next_player()
                return dice1, dice2

        if dice1 == dice2:
            self.doubles_count += 1
            if self.doubles_count == 3:
                print(
                    f"{current_player['name']} rolled three doubles and goes to jail!"
                )
                self.handle_jail(current_player)
                self.advance_to_next_player()
                return dice1, dice2
        else:
            self.doubles_count = 0

        old_pos = current_player["position"]

        new_pos = current_player["position"] + dice1 + dice2
        current_player["position"] = new_pos % 40

        if current_player["position"] == 0:
            current_player["position"] = 40

        if new_pos >= 40 and not self.is_going_to_jail:
            current_player["money"] += 200
            self.bank_money -= 200
            self.completed_circuits[current_player["name"]] += 1
            print(f"{current_player['name']} collected £200 for passing GO")

        result, message = self.handle_space(current_player)
        if result == "bankrupt":
            print(f"{current_player['name']} is bankrupt!")
        elif result == "jail":
            self.doubles_count = 0

        if not dice1 == dice2 or self.is_going_to_jail:
            self.advance_to_next_player()
            self.doubles_count = 0

        return dice1, dice2

    def add_message(self, message):
        self.message_queue.append(message)
        print(f"[GAME] {message}")

    def handle_space(self, player):
        position = str(player["position"])
        if position not in self.properties:
            return None, None

        space = self.properties[position]
        space_type = space.get("type", "")

        if position == "20":
            return "free_parking", None

        if space_type == "special":
            return None, None
        elif space_type == "tax":
            player["money"] -= space["amount"]
            self.bank_money += space["amount"]
            self.add_message(
                f"{player['name']} paid £{space['amount']} {space['name']}"
            )

            if hasattr(self, "game") and self.game:
                self.game.show_tax_popup(player, space["name"], space["amount"])

            return None, None

        if not space.get("owner"):
            if player.get("in_jail", False):
                return None, "Cannot buy property while in jail"

            if not space.get("can_be_bought", False):
                return None, None

            if self.completed_circuits.get(player["name"], 0) < 1:
                return None, None

            self.add_message(
                f"Would you like to buy {space['name']} for £{space['price']}?"
            )
            return "can_buy", None

        elif space["owner"] != player["name"]:
            owner = next((p for p in self.players if p["name"] == space["owner"]), None)
            if owner.get("in_jail", False):
                self.add_message(f"{owner['name']} is in jail and cannot collect rent")
                return None, None

            rent = self.calculate_space_rent(space, player)
            if player["money"] >= rent:
                player["money"] -= rent
                owner["money"] += rent
                message = f"{player['name']} paid £{rent} rent to {owner['name']}"
                self.add_message(message)

                if hasattr(self, "game") and self.game:
                    self.game.show_rent_popup(player, owner, space["name"], rent)
            else:
                message = f"{player['name']} went bankrupt!"
                self.add_message(message)
                self.handle_bankruptcy(player)
                return "bankrupt", message

        return None, None

    def handle_jail(self, player):
        player["position"] = 11
        player["in_jail"] = True
        player["jail_turns"] = 0
        self.is_going_to_jail = True
        self.doubles_count = 0
        self.add_message("Go to jail. Do not pass GO, do not collect £200")
        return "Go to jail. Do not pass GO, do not collect £200"

    def try_leave_jail(self, player, dice1, dice2):
        if not player.get("in_jail", False):
            return True, None

        if "jail_turns" not in player:
            player["jail_turns"] = 0

        if self.jail_free_cards.get(player["name"], 0) > 0 and (
            player.get("is_ai", False)
            or self.game
            and self.game.get_jail_choice(player) == "card"
        ):
            self.jail_free_cards[player["name"]] -= 1
            player["in_jail"] = False
            player["jail_turns"] = 0
            return (
                True,
                f"{player['name']} uses Get Out of Jail Free card and left jail!",
            )

        if dice1 == dice2:
            player["in_jail"] = False
            player["jail_turns"] = 0
            self.doubles_count = 0
            return (
                True,
                f"{player['name']} rolled doubles ({dice1},{dice2}) and left jail!",
            )

        if player["money"] >= 50 and (
            player.get("is_ai", False)
            or self.game
            and self.game.get_jail_choice(player) == "pay"
        ):
            player["money"] -= 50
            self.free_parking_fund += 50
            player["in_jail"] = False
            player["jail_turns"] = 0
            return True, f"{player['name']} paid £50 and left jail"

        player["jail_turns"] += 1

        if player["jail_turns"] >= 3:
            if player["money"] >= 50:
                player["money"] -= 50
                self.free_parking_fund += 50
                player["in_jail"] = False
                player["jail_turns"] = 0
                return True, f"{player['name']} paid £50 after 3 turns and left jail"
            else:
                self.handle_bankruptcy(player)
                player["in_jail"] = False
                player["jail_turns"] = 0
                return (
                    True,
                    f"{player['name']} couldn't pay jail fine and left jail bankrupt",
                )

        return False, f"{player['name']} stays in jail (turn {player['jail_turns']}/3)"

    def check_game_over(self):
        if self.game_mode == "full":
            active_players = [p for p in self.players if p["money"] > 0]
            if len(active_players) <= 1:
                return True, active_players[0] if active_players else None

        elif self.game_mode == "abridged":
            min_rounds = min(self.rounds_completed.values())
            if min_rounds > 0 and all(
                rounds == min_rounds for rounds in self.rounds_completed.values()
            ):
                assets = {}
                for player in self.players:
                    total = player["money"]
                    for prop in self.properties.values():
                        if prop.get("owner") == player["name"]:
                            total += prop["price"]
                            if not prop.get("is_mortgaged", False):
                                total += prop.get("houses", 0) * prop.get(
                                    "house_cost", 0
                                )
                    assets[player["name"]] = total
                winner = max(assets.items(), key=lambda x: x[1])[0]
                return True, winner

        return False, None

    def calculate_space_rent(self, space, player):
        if space.get("is_mortgaged", False):
            return 0

        if "Station" in space["name"]:
            station_count = sum(
                1
                for prop in self.properties.values()
                if "Station" in prop.get("name", "")
                and prop.get("owner") == space["owner"]
            )
            return 25 * (2 ** (station_count - 1))

        elif space["name"] in ["Tesla Power Co", "Edison Water"]:
            utility_count = sum(
                1
                for prop in self.properties.values()
                if prop.get("name") in ["Tesla Power Co", "Edison Water"]
                and prop.get("owner") == space["owner"]
            )
            dice_total = sum(self.last_dice_roll) if self.last_dice_roll else 7
            return dice_total * (10 if utility_count > 1 else 4)

        base_rent = space.get("rent", 0)
        if space.get("houses", 0) > 0:
            house_rents = space.get("house_costs", [])
            house_index = min(space["houses"] - 1, len(house_rents) - 1)
            return house_rents[house_index]

        color_group = space.get("group")
        if color_group:
            all_owned = all(
                p.get("owner") == space["owner"]
                for p in self.properties.values()
                if p.get("group") == color_group
            )
            if all_owned:
                return base_rent * 2

        return base_rent

    def handle_card_draw(self, player, card_type):
        cards = (
            self.pot_luck_cards
            if card_type == "Pot Luck"
            else self.opportunity_knocks_cards
        )
        card = cards.pop(0)
        message = card["text"]
        self.add_message(message)

        if hasattr(self, "game") and self.game and not player.get("is_ai", False):
            self.game.show_card_popup(card_type, message)

        result = None
        if message == "Get out of jail free":
            self.jail_free_cards[player["name"]] = (
                self.jail_free_cards.get(player["name"], 0) + 1
            )
            result = None
        else:
            try:
                action_result, new_bank, new_parking = card["action"](
                    player, self.bank_money, self.free_parking_fund, self
                )
            except TypeError:
                action_result, new_bank, new_parking = card["action"](
                    player, self.bank_money, self.free_parking_fund
                )

            if isinstance(action_result, int) and action_result <= 40:
                old_pos = player["position"]
                player["position"] = action_result
                if action_result < old_pos and action_result != 11:
                    player["money"] += 200
                    self.bank_money -= 200
                    self.add_message("Collected £200 for passing GO")
                result = "moved"
            else:
                print(
                    f"Updating player money from {player['money']} to {action_result}"
                )
                player["money"] = action_result

            self.bank_money = new_bank
            self.free_parking_fund = new_parking

        cards.append(card)
        return result, message

    def calculate_repair_cost(self, player, house_cost, hotel_cost):
        total_cost = 0
        for prop in self.properties.values():
            if prop.get("owner") == player["name"]:
                houses = prop.get("houses", 0)
                if houses == 5:
                    total_cost += hotel_cost
                else:
                    total_cost += houses * house_cost
        return total_cost

    def check_property_group_completion(self, player_name):
        groups = {}
        for prop in self.properties.values():
            if prop.get("group") and prop.get("owner") == player_name:
                groups[prop["group"]] = groups.get(prop["group"], 0) + 1

        group_totals = {}
        for prop in self.properties.values():
            if prop.get("group"):
                group = prop["group"]
                group_totals[group] = group_totals.get(group, 0) + 1

        completed_groups = []
        for group, count in groups.items():
            if group in group_totals and count == group_totals[group]:
                completed_groups.append(group)
                self.add_message(f"🎊 MONOPOLY! 🎊")
                self.add_message(f"{player_name} completed the {group} set!")
                if group not in ["Utilities", "Stations"]:
                    self.add_message(f"Houses can now be built on these properties!")

        return len(completed_groups) > 0

    def buy_property(self, player):
        if player.get("in_jail", False):
            self.add_message(f"{player['name']} cannot buy property while in jail")
            return False

        if self.completed_circuits.get(player["name"], 0) < 1:
            self.add_message(f"{player['name']} must pass GO before buying property")
            return False

        position = str(player["position"])
        property_data = self.properties[position]
        price = property_data["price"]

        if player["money"] >= price:
            if self.validate_bank_transaction(price):
                player["money"] -= price
                self.bank_money += price
                property_data["owner"] = player["name"]
                self.check_property_group_completion(player["name"])
                return True
        return False

    def auction_property(self, position):
        position = str(position)
        print(f"\n=== Starting Auction for Property at Position {position} ===")

        if position not in self.properties:
            self.add_message(f"Error: Invalid property position {position}")
            print(f"Error: Invalid property position {position}")
            return "auction_completed"

        property_data = self.properties[position]
        print(f"Property: {property_data['name']}")

        if property_data.get("type", "") not in ["property", "station", "utility"]:
            self.add_message(f"Error: Cannot auction non-purchasable property")
            print(f"Error: Cannot auction non-purchasable property")
            return "auction_completed"

        eligible_players = [
            p
            for p in self.players
            if not p.get("in_jail", False)
            and not p.get("exited", False)
            and p["money"] >= (property_data["price"] // 2)
        ]

        print(f"Eligible players: {len(eligible_players)}")
        for player in eligible_players:
            print(f"- {player['name']} (Money: £{player['money']})")

        if not eligible_players:
            property_data["owner"] = None
            print("No eligible players for auction - property remains unsold")
            return "auction_completed"

        starting_bid = property_data["price"] // 2
        print(f"Starting bid: £{starting_bid}")

        self.current_auction = {
            "property": property_data,
            "property_position": position,
            "active_players": eligible_players.copy(),
            "passed_players": set(),
            "highest_bidder": None,
            "current_bid": 0,
            "minimum_bid": starting_bid,
            "current_bidder_index": 0,
            "start_time": pygame.time.get_ticks(),
            "duration": 30000,
            "completed": False,
            "message": f"Auction started for {property_data['name']} - Starting bid: £{starting_bid}",
        }

        print(f"Auction initialized with {len(eligible_players)} active players")
        print(f"First bidder: {self.current_auction['active_players'][0]['name']}")
        self.add_message(f"\n🔨 AUCTION: {property_data['name']}")
        self.add_message(f"Starting bid: £{starting_bid}")

        return "auction_in_progress"

    def process_auction_bid(self, player, bid_amount):
        print(f"\n=== Processing Bid: {player['name']} ===")
        print(f"Attempted bid amount: £{bid_amount}")

        if not hasattr(self, "current_auction") or self.current_auction["completed"]:
            print("Error: No active auction")
            return False, "No active auction in progress"

        if player["name"] in self.current_auction["passed_players"]:
            print(f"Error: {player['name']} has already passed")
            return False, "You have already passed on this auction"

        if bid_amount < self.current_auction["minimum_bid"]:
            print(
                f"Error: Bid too low (minimum: £{self.current_auction['minimum_bid']})"
            )
            return False, f"Bid must be at least £{self.current_auction['minimum_bid']}"

        if bid_amount > player["money"]:
            print(f"Error: Insufficient funds (available: £{player['money']})")
            return False, "You don't have enough money"

        current_time = pygame.time.get_ticks()
        remaining_time = max(
            0,
            self.current_auction["start_time"]
            + self.current_auction["duration"]
            - current_time,
        )

        if remaining_time <= 0:
            print("Error: Bid timeout")
            self.current_auction["passed_players"].add(player["name"])
            return (
                False,
                f"{player['name']} took too long to bid - automatically passed",
            )

        print("Bid accepted!")
        print(f"- Previous high bid: £{self.current_auction['current_bid']}")
        print(f"- New high bid: £{bid_amount}")
        print(
            f"- Previous leader: {self.current_auction['highest_bidder']['name'] if self.current_auction['highest_bidder'] else 'None'}"
        )
        print(f"- New leader: {player['name']}")

        self.current_auction["current_bid"] = bid_amount
        self.current_auction["highest_bidder"] = player
        self.current_auction["minimum_bid"] = bid_amount + 10

        self.add_message(f"{player['name']} bids £{bid_amount}")
        self.move_to_next_bidder()
        return True, f"{player['name']} bids £{bid_amount}"

    def process_auction_pass(self, player):
        print(f"\n=== Processing Pass: {player['name']} ===")

        if not hasattr(self, "current_auction") or self.current_auction["completed"]:
            print("Error: No active auction")
            return False, "No active auction in progress"

        if player["name"] in self.current_auction["passed_players"]:
            print(f"Error: {player['name']} has already passed")
            return False, "You have already passed on this auction"

        print(f"{player['name']} passes on bidding")
        self.current_auction["passed_players"].add(player["name"])
        self.add_message(f"{player['name']} passes")

        active_bidders = [
            p
            for p in self.current_auction["active_players"]
            if p["name"] not in self.current_auction["passed_players"]
        ]

        print(f"Active bidders remaining: {len(active_bidders)}")
        for bidder in active_bidders:
            print(f"- {bidder['name']}")

        self.move_to_next_bidder()
        return True, f"{player['name']} passes"

    def check_auction_end(self):
        if not hasattr(self, "current_auction") or not self.current_auction:
            return None

        if self.current_auction.get("completed", False):
            print("Auction is marked as completed - processing outcome")

            property_data = self.current_auction["property"]
            highest_bidder = self.current_auction["highest_bidder"]

            if highest_bidder:
                bid_amount = self.current_auction["current_bid"]
                highest_bidder["money"] -= bid_amount
                self.bank_money += bid_amount
                self.buy_property_after_auction(highest_bidder, property_data)

                result_message = f"{highest_bidder['name']} bought {property_data['name']} for £{bid_amount}"
                print(f"Auction completed - {result_message}")
                self.add_message(result_message)
            else:
                result_message = (
                    f"No one bid on {property_data['name']}, it remains unsold"
                )
                print(f"Auction completed - {result_message}")
                self.add_message(result_message)

            return "auction_completed"

        active_bidders = [
            p
            for p in self.current_auction["active_players"]
            if p["name"] not in self.current_auction["passed_players"]
        ]

        if (
            not active_bidders
            or len(active_bidders) <= 1
            and self.current_auction["highest_bidder"]
        ):
            print(
                "All players have passed or only highest bidder remains - auction is complete"
            )
            self.current_auction["completed"] = True
            return self.check_auction_end()

        current_time = pygame.time.get_ticks()
        if (
            current_time - self.current_auction["start_time"]
            > self.current_auction["duration"]
        ):
            print("Auction timed out - marking as complete")
            self.current_auction["completed"] = True
            return self.check_auction_end()

        return None

    def move_to_next_bidder(self):
        if not hasattr(self, "current_auction"):
            print("Error: No active auction")
            return

        print(f"\n=== Moving to Next Bidder ===")

        active_players = [
            p
            for p in self.current_auction["active_players"]
            if p["name"] not in self.current_auction["passed_players"]
            and p["money"] >= self.current_auction["minimum_bid"]
        ]

        print(f"Active players remaining: {len(active_players)}")
        for player in active_players:
            print(f"- {player['name']} (Money: £{player['money']})")

        if len(active_players) <= 1:
            print("Only one or zero active players remaining")

            if self.current_auction["highest_bidder"]:
                print(
                    f"Auction ending - {self.current_auction['highest_bidder']['name']} wins with bid of £{self.current_auction['current_bid']}"
                )
                self.current_auction["completed"] = True
                return
            elif (
                len(active_players) == 1 and not self.current_auction["highest_bidder"]
            ):
                print(
                    f"One active player remaining ({active_players[0]['name']}) with no current bids - giving them a chance to bid"
                )
                for i, player in enumerate(self.current_auction["active_players"]):
                    if player["name"] == active_players[0]["name"]:
                        self.current_auction["current_bidder_index"] = i
                        break
            else:
                print("No active players or highest bidder - auction will end")
                self.current_auction["completed"] = True
                return
        else:
            current_index = self.current_auction["current_bidder_index"]
            original_index = current_index

            print(f"Current bidder index: {current_index}")
            print(
                f"Current bidder: {self.current_auction['active_players'][current_index]['name']}"
            )

            found_next_bidder = False
            while not found_next_bidder:
                next_index = (current_index + 1) % len(
                    self.current_auction["active_players"]
                )
                next_player = self.current_auction["active_players"][next_index]

                if (
                    next_player["name"] not in self.current_auction["passed_players"]
                    and next_player["money"] >= self.current_auction["minimum_bid"]
                ):
                    found_next_bidder = True
                    self.current_auction["current_bidder_index"] = next_index
                    print(f"Next bidder: {next_player['name']} (index {next_index})")
                    break

                current_index = next_index

                if current_index == original_index:
                    print("Cycled through all players - no eligible bidders found")
                    self.current_auction["completed"] = True
                    return

        self.current_auction["start_time"] = pygame.time.get_ticks()
        print(f"Timer reset for next bidder")

    def is_game_over(self):
        active_players = [
            p for p in self.players if p["money"] > 0 and not p.get("exited", False)
        ]
        return len(active_players) <= 1

    def get_winner(self):
        if self.is_game_over():
            active_players = [
                p for p in self.players if p["money"] > 0 and not p.get("exited", False)
            ]
            if active_players:
                return active_players[0]["name"]
        return None

    def remove_player(self, player_name, voluntary=False):
        player = next((p for p in self.players if p["name"] == player_name), None)
        if player:
            for prop in self.properties.values():
                if prop.get("owner") == player_name:
                    prop["owner"] = None
                    if "houses" in prop:
                        prop["houses"] = 0

            if voluntary:
                player["exited"] = True
                self.voluntary_exits.append(player_name)
            else:
                player["bankrupt"] = True
                self.bankrupted_players.append(player_name)

            if len(self.players) > 0:
                self.current_player_index = self.current_player_index % len(
                    self.players
                )

            return True
        return False

    def auction(self, property_data):
        self.message_queue = [
            msg
            for msg in self.message_queue
            if not msg.startswith("Would you like to buy")
        ]

        auction_message = f"🔨 AUCTION: {property_data['name']} is up for auction!"
        self.add_message(auction_message)

        eligible_players = [
            p
            for p in self.players
            if not p.get("in_jail", False)
            and not p.get("exited", False)
            and p["money"] >= (property_data["price"] // 2)
        ]

        if not eligible_players:
            self.add_message(
                f"No eligible players for auction. {property_data['name']} remains unsold."
            )
            property_data["owner"] = None
            return

        winning_bid_info = self.placeBids(eligible_players, property_data)

        if not winning_bid_info:
            self.add_message(f"{property_data['name']} remains unsold")
            property_data["owner"] = None
        else:
            winner, bid = winning_bid_info
            if winner["money"] >= bid:
                winner["money"] -= bid
                self.bank_money += bid
                property_data["owner"] = winner["name"]
                self.add_message(
                    f"🎊 {winner['name']} won {property_data['name']} for £{bid}"
                )
                self.check_property_group_completion(winner["name"])
            else:
                self.add_message(
                    f"Error: {winner['name']} cannot afford the winning bid"
                )
                property_data["owner"] = None

    def placeBids(self, player_list, property_data):
        print("\n=== Property Auction Debug ===")
        print(f"Starting auction for {property_data['name']}")
        print(f"Property position: {property_data.get('position', 'Unknown')}")
        print(f"Starting price: £{property_data['price'] // 2}")

        current_minimum = property_data["price"] // 2
        active_players = player_list[:]
        current_bids = {}
        round_count = 1

        while len(active_players) > 1:
            print(f"\n=== Auction Round {round_count} ===")
            print(f"Active players: {[p['name'] for p in active_players]}")
            print(f"Current minimum bid: £{current_minimum}")

            round_bids = {}
            for player in active_players[:]:
                print(f"\nPlayer {player['name']}'s turn")
                print(f"Available money: £{player['money']}")

                if player.get("in_jail", False):
                    print(f"{player['name']} is in jail - skipping")
                    active_players.remove(player)
                    continue

                bid = None
                if player.get("is_ai", False):
                    bid = self.get_ai_bid(player, current_minimum, property_data)
                    if bid:
                        print(f"AI {player['name']} bids £{bid}")
                        self.add_message(f"AI {player['name']} bids £{bid}")
                    else:
                        print(f"AI {player['name']} passes")
                        self.add_message(f"AI {player['name']} passes")
                        active_players.remove(player)
                else:
                    current_bids[player["name"]] = current_minimum
                    continue

                if bid and bid >= current_minimum and bid <= player["money"]:
                    round_bids[player["name"]] = bid
                    current_bids[player["name"]] = bid
                else:
                    if player in active_players:
                        active_players.remove(player)

            if not round_bids and not any(
                p for p in active_players if not p.get("is_ai", False)
            ):
                print("\nNo valid bids this round")
                break

            if round_bids:
                highest_bid = max(round_bids.values())
                highest_bidders = [
                    p
                    for p in active_players
                    if round_bids.get(p["name"], 0) == highest_bid
                ]

                print(f"\nRound {round_count} Results:")
                print(f"Highest bid: £{highest_bid}")
                print(f"Highest bidders: {[p['name'] for p in highest_bidders]}")

                active_players = highest_bidders
                current_minimum = highest_bid + 10

            round_count += 1

        winner = None
        final_bid = 0

        if len(active_players) == 1:
            winner = active_players[0]
            final_bid = current_bids.get(winner["name"], current_minimum)

        if winner:
            print(f"\n=== Auction Complete ===")
            print(f"Winner: {winner['name']}")
            print(f"Winning bid: £{final_bid}")
            return winner, final_bid

        print("\nAuction ended with no winner")
        return None

    def get_ai_bid(self, player, current_minimum, property_data):
        print(f"\n=== AI Bid Evaluation ===")
        print(f"AI Player: {player['name']}")
        print(f"Property: {property_data['name']}")
        print(f"Current minimum: £{current_minimum}")
        print(f"Available money: £{player['money']}")

        if player["money"] < current_minimum:
            print("DECISION: Cannot bid - insufficient funds")
            return None

        base_value = property_data["price"]
        value_multiplier = 1.0

        print(f"Base value assessment:")
        print(f"- Property price: £{base_value}")

        if "group" in property_data:
            owned_in_group = sum(
                1
                for p in self.properties.values()
                if p.get("group") == property_data["group"]
                and p.get("owner") == player["name"]
            )
            total_in_group = sum(
                1
                for p in self.properties.values()
                if p.get("group") == property_data["group"]
            )

            print(f"Group analysis:")
            print(f"- Group: {property_data['group']}")
            print(f"- Owned in group: {owned_in_group}/{total_in_group}")

            if owned_in_group > 0:
                group_bonus = 0.3 * (owned_in_group / total_in_group)
                value_multiplier += group_bonus
                print(f"- Adding group bonus: +{group_bonus:.2f}x")

        if "Station" in property_data["name"]:
            owned_stations = sum(
                1
                for p in self.properties.values()
                if "Station" in p.get("name", "") and p.get("owner") == player["name"]
            )
            station_bonus = 0.25 * owned_stations
            value_multiplier += station_bonus
            print(f"Station analysis:")
            print(f"- Owned stations: {owned_stations}")
            print(f"- Adding station bonus: +{station_bonus:.2f}x")

        elif property_data["name"] in ["Tesla Power Co", "Edison Water"]:
            owned_utilities = sum(
                1
                for p in self.properties.values()
                if p.get("name") in ["Tesla Power Co", "Edison Water"]
                and p.get("owner") == player["name"]
            )
            print(f"Utility analysis:")
            print(f"- Owned utilities: {owned_utilities}")
            if owned_utilities > 0:
                value_multiplier += 0.5
                print("- Adding utility bonus: +0.5x")

        perceived_value = base_value * value_multiplier
        print(f"\nValue calculation:")
        print(f"- Base value: £{base_value}")
        print(f"- Final multiplier: {value_multiplier:.2f}x")
        print(f"- Perceived value: £{perceived_value}")

        max_bid = min(player["money"], perceived_value)
        print(f"Maximum possible bid: £{max_bid}")

        if max_bid <= current_minimum:
            print("DECISION: Pass - maximum bid below minimum")
            return None

        import random

        bid_headroom = max_bid - current_minimum
        increment = min(50, max(10, int(bid_headroom * 0.2)))
        bid = current_minimum + random.randint(10, increment)
        bid = min(bid, max_bid)

        print(f"Bid calculation:")
        print(f"- Bid headroom: £{bid_headroom}")
        print(f"- Chosen increment: £{increment}")
        print(f"- Initial bid: £{bid}")

        if bid > perceived_value * 0.8:
            risky_bid_chance = random.random()
            print(f"\nRisk assessment:")
            print(f"- Bid (£{bid}) is above 80% of perceived value")
            print(f"- Risk check: {risky_bid_chance:.2f} (will pass if < 0.3)")
            if risky_bid_chance < 0.3:
                print("DECISION: Pass due to risk assessment")
                return None

        print(f"FINAL DECISION: Bid £{bid}")
        return bid

    def get_human_bid(self, player, current_minimum, property_data):
        import time

        self.add_message(
            f"Player {player['name']}, would you like to bid? (Yes/No) Current minimum bid: £{current_minimum}"
        )
        start_time = time.time()
        while True:
            try:
                response = input(
                    f"{player['name']}, enter 'Yes' or 'No' (30s timeout): "
                )
            except Exception as e:
                self.add_message(f"Error: {e}")
                return None
            if time.time() - start_time > 30:
                self.add_message(
                    f"Timeout: {player['name']} did not respond in time, skipping bid"
                )
                return None
            if response.strip().lower() == "no":
                return None
            elif response.strip().lower() == "yes":
                try:
                    bid_input = input(
                        f"{player['name']}, what is your bid? (Enter amount): "
                    )
                    if time.time() - start_time > 30:
                        self.add_message(
                            f"Timeout: {player['name']} took too long to enter bid amount"
                        )
                        return None
                    bid = int(bid_input)
                    if bid < current_minimum:
                        self.add_message(f"Bid must be at least £{current_minimum}")
                        start_time = time.time()
                        continue
                    if bid > player["money"]:
                        self.add_message(f"Insufficient funds")
                        return None
                    return bid
                except Exception as e:
                    self.add_message(f"Error processing bid: {e}")
                    return None
            else:
                self.add_message("Please enter 'Yes' or 'No'")
                start_time = time.time()
                continue

    def buy_property_after_auction(self, player, property_data):
        if self.completed_circuits.get(player["name"], 0) < 1:
            self.add_message(f"{player['name']} must pass GO before buying property")
            return False

        position = str(property_data.get("position", ""))
        if position in self.properties:
            self.properties[position]["owner"] = player["name"]
            if "properties" not in player:
                player["properties"] = []
            player["properties"].append(property_data["name"])
            self.add_message(f"{player['name']} now owns {property_data['name']}.")
            self.check_property_group_completion(player["name"])
            return True
        else:
            print(f"Warning: Property position {position} not found in properties list")
            return False

    def handle_bankruptcy(self, player):
        total_liquidated = 0
        property_list = []

        for prop in self.properties.values():
            if prop.get("owner") == player["name"]:
                value = prop["price"]
                if "houses" in prop and prop["houses"] > 0:
                    house_costs = prop.get("house_costs", [])
                    if house_costs and isinstance(house_costs, list):
                        house_value = sum(house_costs[: prop["houses"]])
                    else:
                        house_value = 0
                    value += house_value
                property_list.append((prop["name"], value))
                total_liquidated += value

        if property_list:
            self.add_message(f"🏦 Liquidating {player['name']}'s properties:")
            for prop_name, value in property_list:
                self.add_message(f"- {prop_name}: £{value}")
            self.add_message(f"Total liquidated: £{total_liquidated}")

        for prop in self.properties.values():
            if prop.get("owner") == player["name"]:
                prop["owner"] = None
                if "houses" in prop:
                    prop["houses"] = 0

        player["bankrupt"] = True
        self.players.remove(player)
        self.bankrupted_players.append(player["name"])

        if len(self.players) > 0:
            self.current_player_index = self.current_player_index % len(self.players)

        return True

    def can_build_house(self, property_data, player):
        print(f"\n=== DEBUG: can_build_house CHECK ===")
        print(f"Property: {property_data.get('name', 'Unknown')}")
        print(f"Player: {player['name'] if player else 'None'}")
        print(f"Property position: {property_data.get('position', 'Unknown')}")

        if property_data.get("is_mortgaged", False):
            print("Cannot build - property is mortgaged")
            return False, "Cannot build on mortgaged property"

        color_group = property_data.get("group")
        print(f"Color group: {color_group}")

        if not color_group:
            print("Cannot build - not a valid property group")
            return False, "Cannot build houses on this type of property"

        color_group_properties = [
            p for p in self.properties.values() if p.get("group") == color_group
        ]

        print(f"Total properties in group: {len(color_group_properties)}")
        for prop in color_group_properties:
            prop_owner = prop.get("owner", "None")
            print(
                f"  - {prop.get('name', 'Unknown')} (Position: {prop.get('position', 'Unknown')}, Owner: {prop_owner})"
            )

            if prop.get("owner") != player["name"]:
                print(
                    f"Cannot build - {prop.get('name', 'Unknown')} is owned by {prop.get('owner', 'None')}, not {player['name']}"
                )
                return False, f"Must own all {color_group} properties to build"

        current_houses = property_data.get("houses", 0)
        print(f"Current houses on property: {current_houses}")

        for prop in color_group_properties:
            if prop != property_data:
                other_houses = prop.get("houses", 0)
                print(f"  - {prop.get('name', 'Unknown')} has {other_houses} houses")

                if current_houses + 1 > other_houses + 1:
                    print(
                        f"Cannot build - houses must be built evenly. This property would have {current_houses + 1} houses while {prop.get('name', 'Unknown')} has {other_houses}"
                    )
                    return False, "Must build houses evenly across properties"

        if current_houses >= 5:
            print("Cannot build - maximum development reached")
            return False, "Maximum development reached"

        print("Can build house: YES")
        return True, None

    def can_build_hotel(self, property_data, player):
        if not self.check_property_group_completion(player["name"]):
            return False, "You must own all properties in the color group"

        color_group = [
            p
            for p in self.properties.values()
            if p.get("color") == property_data.get("color")
            and p.get("owner") == player["name"]
        ]

        current_houses = property_data.get("houses", 0)
        if current_houses != 4:
            return False, "Must have 4 houses before building a hotel"

        for prop in color_group:
            if prop != property_data:
                other_houses = prop.get("houses", 0)
                if other_houses < 4:
                    return (
                        False,
                        "All properties in the set must have at least 4 houses before building a hotel",
                    )

        return True, None

    def build_house(self, property_data, player):
        can_build, error = self.can_build_house(property_data, player)
        if not can_build:
            self.add_message(error)
            return False

        current_houses = property_data.get("houses", 0)
        if current_houses >= self.MAX_HOUSES_PER_PROPERTY:
            self.add_message("Maximum number of houses already built")
            return False

        house_cost = property_data.get("house_cost", 0)
        if player["money"] >= house_cost:
            if self.validate_bank_transaction(house_cost):
                player["money"] -= house_cost
                self.bank_money += house_cost
                property_data["houses"] = current_houses + 1
                self.add_message(
                    f"{player['name']} built a house on {property_data['name']}"
                )
                return True

        self.add_message("Not enough money to build a house")
        return False

    def build_hotel(self, property_data, player):
        can_build, error = self.can_build_hotel(property_data, player)
        if not can_build:
            self.add_message(error)
            return False

        hotel_cost = property_data.get("house_cost", 0)
        if player["money"] >= hotel_cost:
            if self.validate_bank_transaction(hotel_cost):
                player["money"] -= hotel_cost
                self.bank_money += hotel_cost
                property_data["houses"] = 5
                self.add_message(
                    f"{player['name']} built a hotel on {property_data['name']}"
                )
                return True

        self.add_message("Not enough money to build a hotel")
        return False

    def sell_house(self, property_data, player):
        current_houses = property_data.get("houses", 0)
        if current_houses == 0:
            self.add_message("No houses to sell")
            return False

        color_group = [
            p
            for p in self.properties.values()
            if p.get("color") == property_data.get("color")
            and p.get("owner") == player["name"]
        ]

        for prop in color_group:
            if prop != property_data:
                other_houses = prop.get("houses", 0)
                if current_houses - 1 < other_houses - 1:
                    self.add_message(
                        "Cannot have more than 1 house difference between properties in a set"
                    )
                    return False

        house_cost = property_data.get("house_cost", 0)
        player["money"] += house_cost // 2
        self.bank_money -= house_cost // 2
        property_data["houses"] = current_houses - 1
        self.add_message(f"{player['name']} sold a house from {property_data['name']}")
        return True

    def sell_hotel(self, property_data, player):
        if property_data.get("houses", 0) != 5:
            self.add_message("No hotel to sell")
            return False

        hotel_cost = property_data.get("house_cost", 0) * 5
        player["money"] += hotel_cost // 2
        self.bank_money -= hotel_cost // 2
        property_data["houses"] = 4
        self.add_message(f"{player['name']} sold a hotel from {property_data['name']}")
        return True

    def mortgage_property(self, property_data, player):
        if property_data.get("is_mortgaged", False):
            self.add_message(f"{property_data['name']} is already mortgaged")
            return False

        if property_data.get("houses", 0) > 0:
            self.add_message("Cannot mortgage property with houses/hotels")
            return False

        mortgage_value = property_data["price"] // 2
        self.pay_from_bank(player, mortgage_value)
        property_data["is_mortgaged"] = True
        self.add_message(
            f"{player['name']} mortgaged {property_data['name']} for £{mortgage_value}"
        )
        return True

    def unmortgage_property(self, property_data, player):
        if not property_data.get("is_mortgaged", False):
            self.add_message(f"{property_data['name']} is not mortgaged")
            return False

        unmortgage_cost = (property_data["price"] // 2) * 1.1
        if player["money"] >= unmortgage_cost:
            self.pay_to_bank(player, unmortgage_cost)
            property_data["is_mortgaged"] = False
            self.add_message(
                f"{player['name']} unmortgaged {property_data['name']} for £{unmortgage_cost}"
            )
            return True
        else:
            self.add_message(f"Not enough money to unmortgage {property_data['name']}")
            return False

    def handle_rent_payment(self, landing_player, property_data):
        if property_data.get("is_mortgaged", False):
            self.add_message(f"Property is mortgaged - no rent due")
            return True

        owner = next(
            (p for p in self.players if p["name"] == property_data["owner"]), None
        )
        if not owner or owner.get("in_jail", False):
            self.add_message(f"Owner is in jail - no rent collected")
            return True

        rent = self.calculate_space_rent(property_data, landing_player)
        if landing_player["money"] >= rent:
            landing_player["money"] -= rent
            owner["money"] += rent
            self.add_message(
                f"{landing_player['name']} paid £{rent} rent to {owner['name']}"
            )

            if hasattr(self, "game") and self.game:
                self.game.show_rent_popup(
                    landing_player, owner, property_data["name"], rent
                )

            return True
        else:
            self.handle_bankruptcy(landing_player)
            return False

    def calculate_house_difference(self, color_group_properties):
        house_counts = [p.get("houses", 0) for p in color_group_properties]
        return max(house_counts) - min(house_counts)

    def handle_ai_turn(self, player):
        if not player.get("is_ai", False):
            return None

        if player.get("in_jail", False):
            jail_decision = self.ai_player.get_jail_decision(
                player, *self.last_dice_roll
            )
            if (
                jail_decision == "use_card"
                and self.jail_free_cards.get(player["name"], 0) > 0
            ):
                self.jail_free_cards[player["name"]] -= 1
                player["in_jail"] = False
                player["jail_turns"] = 0
            elif jail_decision == "pay" and player["money"] >= 50:
                player["money"] -= 50
                self.free_parking_fund += 50
                player["in_jail"] = False
                player["jail_turns"] = 0

        owned_properties = [
            prop
            for prop in self.properties.values()
            if prop.get("owner") == player["name"]
        ]
        development_priorities = self.ai_player.get_development_priority(
            owned_properties
        )

        for property_data, _ in development_priorities:
            if self.ai_player.should_develop_property(
                property_data, player["money"], owned_properties
            ):
                if property_data.get("houses", 0) == 4:
                    self.build_hotel(property_data, player)
                else:
                    self.build_house(property_data, player)

        if player["money"] < 200:
            for prop in owned_properties:
                if self.ai_player.should_mortgage_property(prop, player["money"]):
                    self.mortgage_property(prop, player)
        elif player["money"] > 500:
            mortgaged_properties = [
                p for p in owned_properties if p.get("is_mortgaged", True)
            ]
            for prop in mortgaged_properties:
                if self.ai_player.should_unmortgage_property(prop, player["money"]):
                    self.unmortgage_property(prop, player)

        return None

    def process_ai_property_purchase(self, player, property_data):
        if not player.get("is_ai", False):
            return False

        owned_properties = [
            prop
            for prop in self.properties.values()
            if prop.get("owner") == player["name"]
        ]
        if self.ai_player.should_buy_property(
            property_data, player["money"], owned_properties
        ):
            if property_data["price"] <= player["money"]:
                self.pay_to_bank(player, property_data["price"])
                property_data["owner"] = player["name"]
                self.add_message(
                    f"{player['name']} buys {property_data['name']} for £{property_data['price']}"
                )
                return True
        return False

    def get_ai_auction_bid(self, player, property_data, current_bid):
        if not player.get("is_ai", False):
            return None

        try:
            print(f"\n=== AI Auction Bid Logic ===")
            print(f"AI Player: {player['name']}")
            print(f"Property: {property_data['name']}")
            print(f"Current bid: £{current_bid}")
            print(f"Player money: £{player['money']}")

            minimum_bid = max(current_bid + 10, property_data["price"] // 2)
            if player["money"] < minimum_bid:
                print(f"AI can't afford minimum bid of £{minimum_bid}")
                return None

            owned_properties = [
                prop
                for prop in self.properties.values()
                if prop.get("owner") == player["name"]
            ]

            bid_amount = self.ai_player.make_auction_bid(
                property_data, current_bid, player["money"], owned_properties
            )

            if (
                bid_amount
                and bid_amount > current_bid
                and bid_amount <= player["money"]
            ):
                bid_amount = max(bid_amount, current_bid + 10)
                print(f"AI {player['name']} decided to bid £{bid_amount}")
                return bid_amount
            else:
                print(f"AI {player['name']} decided to pass")
                return None
        except Exception as e:
            print(f"Error in AI auction bidding: {e}")
            return None

    def handle_ai_bankruptcy_prevention(self, player, amount_needed):

        owned_properties = [
            prop
            for prop in self.properties.values()
            if prop.get("owner") == player["name"]
        ]
        if not owned_properties:
            return False

        for prop in owned_properties:
            while prop.get("houses", 0) > 0 and player["money"] < amount_needed:
                if prop.get("houses", 0) == 5:
                    self.sell_hotel(prop, player)
                    self.add_message(
                        f"{player['name']} sold hotel on {prop['name']} to raise funds"
                    )
                else:
                    self.sell_house(prop, player)
                    self.add_message(
                        f"{player['name']} sold house on {prop['name']} to raise funds"
                    )
                if player["money"] >= amount_needed:
                    return True

        for prop in owned_properties:
            if not prop.get("is_mortgaged", False) and player["money"] < amount_needed:
                if prop.get("houses", 0) == 0:
                    self.mortgage_property(prop, player)
                    self.add_message(
                        f"{player['name']} mortgaged {prop['name']} to raise funds"
                    )
                    if player["money"] >= amount_needed:
                        return True

        return player["money"] >= amount_needed

    def handle_buy_decision(self, player, decision):
        position = str(player["position"])
        property_data = self.properties[position]

        if player.get("in_jail", False):
            return "Cannot buy property while in jail"

        if property_data.get("owner") is not None:
            return "Property is already owned"

        if property_data.get("is_mortgaged", False):
            return "Property is mortgaged and cannot be purchased"

        print("\n=== Property Purchase Decision ===")
        print(f"Property: {property_data['name']}")
        print(f"Player: {player['name']}")
        print(f"Decision: {decision}")

        if player.get("is_ai", False):
            if self.process_ai_property_purchase(player, property_data):
                self.add_message(f"{player['name']} bought {property_data['name']}")
                return "purchase_completed"
            else:
                self.add_message(f"\n{property_data['name']} goes to auction!")
                self.auction_property(position)
                return "auction_started"

        if decision == "buy":
            if self.buy_property(player):
                self.add_message(f"{player['name']} bought {property_data['name']}")
                return "purchase_completed"
            else:
                self.add_message(
                    f"\nInsufficient funds - {property_data['name']} goes to auction!"
                )
                self.auction_property(position)
                return "auction_started"
        elif decision == "auction":
            self.add_message(
                f"\n{player['name']} declined to buy {property_data['name']}"
            )
            self.auction_property(position)
            return "auction_started"
        else:
            return "Invalid decision. Must be 'buy' or 'auction'"

    def handle_birthday_collection(self, birthday_player):

        total_collected = 0
        self.add_message(
            f"\n🎂 {birthday_player['name']}'s Birthday! Each player must pay £10"
        )

        for player in self.players:
            if player["name"] == birthday_player["name"]:
                continue

            self.add_message(f"\n{player['name']} needs to pay £10")
            if player["money"] >= 10:
                player["money"] -= 10
                total_collected += 10
                self.add_message(f"{player['name']} paid £10")
            else:
                needed_amount = 10 - player["money"]
                self.add_message(f"{player['name']} needs to raise £{needed_amount}")

                success = self.handle_ai_bankruptcy_prevention(player, needed_amount)

                if player["money"] >= 10:
                    player["money"] -= 10
                    total_collected += 10
                    self.add_message(f"{player['name']} raised funds and paid £10")
                else:
                    self.add_message(f"{player['name']} cannot pay and goes bankrupt")
                    self.handle_bankruptcy(player)
                    if player["money"] > 0:
                        total_collected += player["money"]
                        player["money"] = 0

        birthday_player["money"] += total_collected
        self.add_message(
            f"\n{birthday_player['name']} collected £{total_collected} in total!"
        )

        return birthday_player["money"], self.bank_money, self.free_parking_fund

    def handle_payment_to_bank(self, player, amount, to_free_parking=False):

        self.add_message(f"\n{player['name']} needs to pay £{amount}")

        if player["money"] >= amount:
            player["money"] -= amount
            if to_free_parking:
                self.free_parking_fund += amount
            else:
                self.bank_money += amount
            self.add_message(f"{player['name']} paid £{amount}")
            return player["money"], self.bank_money, self.free_parking_fund
        else:
            needed_amount = amount - player["money"]
            self.add_message(f"{player['name']} needs to raise £{needed_amount}")

            success = self.handle_ai_bankruptcy_prevention(player, needed_amount)

            if player["money"] >= amount:
                player["money"] -= amount
                if to_free_parking:
                    self.free_parking_fund += amount
                else:
                    self.bank_money += amount
                self.add_message(f"{player['name']} raised funds and paid £{amount}")
            else:
                self.add_message(f"{player['name']} cannot pay and goes bankrupt")
                remaining_money = player["money"]
                self.handle_bankruptcy(player)
                if remaining_money > 0:
                    if to_free_parking:
                        self.free_parking_fund += remaining_money
                    else:
                        self.bank_money += remaining_money

            return player["money"], self.bank_money, self.free_parking_fund

    def handle_repair_assessment(self, player, house_cost, hotel_cost):

        repair_cost = self.calculate_repair_cost(player, house_cost, hotel_cost)

        if repair_cost > 0:
            self.add_message(
                f"\n{player['name']} is assessed £{repair_cost} for repairs (£{house_cost}/house, £{hotel_cost}/hotel)"
            )
            return self.handle_payment_to_bank(player, repair_cost)
        else:
            self.add_message(
                f"{player['name']} has no houses or hotels - no repair costs"
            )
            return player["money"], self.bank_money, self.free_parking_fund
