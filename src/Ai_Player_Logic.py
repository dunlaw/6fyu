# Property Tycoon ai_player_logic.py
# It contains the classes for the AI players, such as the AI player logic, the AI player strategy, and the AI player actions.

import random
from src.Property import Property
from src.Player import Player


class EasyAIPlayer:
    def __init__(self, difficulty="easy"):
        self.difficulty = "easy"
        self.strategy = {
            "easy": {
                "max_bid_multiplier": 0.8,
                "development_threshold": 0.7,
                "jail_stay_threshold": 0.3,
                "mortgage_threshold": 0.2,
            }
        }

    def get_group_properties(self, color_group, board_properties):
        return [
            prop
            for prop in board_properties
            if hasattr(prop, "group") and prop.group == color_group
        ]

    def check_group_ownership(self, color_group, board_properties, player_name):
        if not color_group:
            return False

        group_properties = [
            p
            for p in board_properties
            if hasattr(p, "group") and p.group == color_group
        ]
        return all(p.owner == player_name for p in group_properties)

    def can_build_house(self, property, color_group_properties):
        if property.houses >= 4:
            return False

        min_houses = min(prop.houses for prop in color_group_properties)
        return property.houses <= min_houses

    def get_property_value(self, property_data, ai_player, board_properties):
        print("\n=== AI Property Value Calculation Debug ===")
        print(
            f"Evaluating property: {property_data.name if hasattr(property_data, 'name') else 'Unknown'}"
        )

        base_value = property_data.price
        multiplier = 1.0
        print(f"Base value: £{base_value}")

        if hasattr(property_data, "group"):
            owned_in_group = sum(
                1
                for p in board_properties
                if hasattr(p, "group")
                and p.group == property_data.group
                and p.owner == ai_player
            )
            total_in_group = sum(
                1
                for p in board_properties
                if hasattr(p, "group") and p.group == property_data.group
            )
            print(f"Color group analysis:")
            print(f"- Group: {property_data.group}")
            print(f"- Owned in group: {owned_in_group}/{total_in_group}")

            if owned_in_group > 0:
                group_bonus = 0.3 * (owned_in_group / total_in_group)
                multiplier += group_bonus
                print(f"- Adding group ownership bonus: +{group_bonus:.2f}x")

        if property_data.is_station:
            owned_stations = sum(
                1 for p in board_properties if p.is_station and p.owner == ai_player
            )
            station_bonus = 0.25 * owned_stations
            multiplier += station_bonus
            print(f"Station analysis:")
            print(f"- Owned stations: {owned_stations}")
            print(f"- Adding station bonus: +{station_bonus:.2f}x")

        elif property_data.is_utility:
            owned_utilities = sum(
                1 for p in board_properties if p.is_utility and p.owner == ai_player
            )
            print(f"Utility analysis:")
            print(f"- Owned utilities: {owned_utilities}")
            if owned_utilities > 0:
                multiplier += 0.5
                print("- Adding utility bonus: +0.5x")

        final_value = base_value * multiplier
        print(f"Final calculations:")
        print(f"- Total multiplier: {multiplier:.2f}x")
        print(f"- Final perceived value: £{final_value:.2f}")
        return final_value

    def handle_turn(
        self, ai_player, current_location, board_properties, is_first_round=False
    ):
        actions = {"bought_property": False, "built_house": False, "paid_rent": False}

        if current_location.name == "GO":
            return actions

        elif isinstance(current_location, Property):
            if current_location.owner and current_location.owner != ai_player:
                rent = current_location.calculate_rent(
                    None, current_location.owner.properties
                )
                if ai_player.money >= rent:
                    actions["paid_rent"] = True

            elif not current_location.owner:
                if random.random() < 0.7 and ai_player.money >= current_location.price:
                    success = ai_player.buy_property(current_location)
                    actions["bought_property"] = success

                    if (
                        success
                        and not is_first_round
                        and hasattr(current_location, "group")
                    ):
                        color_group = current_location.group
                        if self.check_group_ownership(
                            color_group, board_properties, ai_player.name
                        ):
                            if random.random() < 0.5:
                                group_properties = self.get_group_properties(
                                    color_group, board_properties
                                )
                                if self.can_build_house(
                                    current_location, group_properties
                                ):
                                    house_cost = current_location.price / 2
                                    if ai_player.money >= house_cost:
                                        current_location.houses += 1
                                        ai_player.pay(house_cost)
                                        actions["built_house"] = True

        elif current_location.name == "JAIL":
            pass

        elif current_location.name == "FREE PARKING":
            pass

        return actions

    def should_use_get_out_of_jail_card(self):
        return True

    def should_pay_jail_fine(self, ai_player):
        return ai_player.money >= 250

    def should_mortgage_property(self, ai_player, required_money):
        if ai_player.money >= required_money:
            return []

        to_mortgage = []
        need_amount = required_money - ai_player.money

        unset_properties = [
            prop
            for prop in ai_player.properties
            if not self.check_group_ownership(
                prop.group, ai_player.properties, ai_player.name
            )
        ]

        for prop in sorted(unset_properties, key=lambda x: x.price):
            if need_amount <= 0:
                break
            if not prop.is_mortgaged:
                to_mortgage.append(prop)
                need_amount -= prop.price / 2

        if need_amount > 0:
            set_properties = [
                prop
                for prop in ai_player.properties
                if self.check_group_ownership(
                    prop.group, ai_player.properties, ai_player.name
                )
            ]

            for prop in sorted(set_properties, key=lambda x: x.price):
                if need_amount <= 0:
                    break
                if not prop.is_mortgaged:
                    to_mortgage.append(prop)
                    need_amount -= prop.price / 2

        return to_mortgage

    def handle_ai_turn(self, ai_player, board_properties):
        current_location_type = self.get_location_type(
            ai_player.position, board_properties
        )
        property_name = self.get_property_name(ai_player.position, board_properties)

        if current_location_type == "Go":
            return True

        elif current_location_type == "property":
            property_data = next(
                (p for p in board_properties if p.name == property_name), None
            )
            if not property_data:
                return True

            if property_data.owner and property_data.owner != ai_player:
                return True
            elif not property_data.owner:
                if random.random() < 0.7 and ai_player.money >= property_data.price:
                    return True
                return False

        elif current_location_type == "lucky_area":
            return True

        elif current_location_type == "jail":
            return True

        return True

    def get_location_type(self, position, board_properties):
        property_data = next(
            (p for p in board_properties if p.position == position), None
        )

        if not property_data:
            if position == 1:
                return "Go"
            elif position == 11:
                return "jail"
            elif position == 21:
                return "free_parking"
            elif position in [3, 18, 34]:
                return "lucky_area"
            elif position in [8, 23, 37]:
                return "lucky_area"
            return "other"

        return "property"

    def get_property_name(self, position, board_properties):
        property_data = next(
            (p for p in board_properties if p.position == position), None
        )
        return property_data.name if property_data else None

    def get_auction_bid(
        self, current_minimum, property_data, ai_player, board_properties
    ):
        if hasattr(self, "last_bid_property"):
            if self.last_bid_property != property_data["name"]:
                self.last_bid_amount = 0
                self.last_bid_property = property_data["name"]
        else:
            self.last_bid_amount = 0
            self.last_bid_property = property_data["name"]

        print("\n=== AI Auction Bid Logic Debug ===")
        print(f"AI Player: {ai_player}")
        print(f"Current minimum bid: £{current_minimum}")
        print(f"Available money: £{ai_player.money}")
        print(f"Previous bid on this property: £{self.last_bid_amount}")

        if ai_player.money < current_minimum:
            print("DECISION: Cannot bid - insufficient funds")
            return None

        perceived_value = self.get_property_value(
            property_data, ai_player, board_properties
        )
        max_bid = min(
            ai_player.money,
            perceived_value * self.strategy["easy"]["max_bid_multiplier"],
        )

        if self.last_bid_amount >= max_bid * 0.8:
            print("DECISION: Already reached maximum desired bid")
            return None

        print(f"\nBid limit calculation:")
        print(f"- Perceived value: £{perceived_value}")
        print(
            f"- Easy difficulty multiplier: {self.strategy['easy']['max_bid_multiplier']}x"
        )
        print(f"- Maximum possible bid: £{max_bid}")

        if max_bid <= current_minimum:
            print("DECISION: Cannot bid - maximum possible bid is below minimum")
            return None

        bid_headroom = max_bid - current_minimum
        increment = min(50, max(10, int(bid_headroom * 0.2)))
        print(f"\nBid increment analysis:")
        print(f"- Bid headroom: £{bid_headroom}")
        print(f"- Calculated increment: £{increment}")

        import random

        bid = current_minimum + random.randint(10, increment)
        bid = min(bid, max_bid)
        print(f"- Initial bid calculation: £{bid}")

        if bid > perceived_value * 0.6:
            risky_bid_chance = random.random()
            print(f"\nRisk assessment:")
            print(
                f"- Bid (£{bid}) is above 60% of perceived value (£{perceived_value * 0.6:.2f})"
            )
            print(
                f"- Random chance to pass: {risky_bid_chance:.2f} (will pass if < 0.3)"
            )
            if risky_bid_chance < 0.3:
                print("DECISION: Passing due to risk assessment")
                return None

        self.last_bid_amount = bid
        print(f"FINAL DECISION: Bidding £{bid}")
        return bid

    def handle_jail_strategy(self, ai_player, jail_free_cards):
        if not ai_player.get("in_jail", False):
            return None

        if jail_free_cards.get(ai_player["name"], 0) > 0:
            return "use_card"

        if ai_player["money"] >= 250:
            total_property_value = sum(prop["price"] for prop in ai_player.properties)
            if total_property_value > 500:
                return "pay_fine"

        return "roll_doubles"

    def handle_property_development(self, ai_player, board_properties):
        if ai_player["money"] < 200:
            return None

        groups = set()
        for prop in board_properties.values():
            if "group" in prop:
                groups.add(prop["group"])

        for color_group in groups:
            group_properties = [
                p
                for p in board_properties.values()
                if p.get("group") == color_group and p.get("owner") == ai_player["name"]
            ]

            total_in_group = sum(
                1 for p in board_properties.values() if p.get("group") == color_group
            )

            if len(group_properties) == total_in_group:
                for prop in group_properties:
                    current_houses = prop.get("houses", 0)
                    if current_houses < 4:
                        min_houses = min(p.get("houses", 0) for p in group_properties)
                        if current_houses <= min_houses:
                            house_cost = prop["price"] / 2
                            if ai_player["money"] >= house_cost * 1.5:
                                return prop
        return None

    def handle_emergency_cash(self, ai_player, required_amount, board_properties):
        if ai_player["money"] >= required_amount:
            return []

        properties_to_mortgage = []
        for prop in board_properties.values():
            if prop.get("owner") == ai_player["name"] and not prop.get("is_mortgaged"):
                if not self.check_group_ownership(
                    prop.get("group"), board_properties, ai_player["name"]
                ):
                    properties_to_mortgage.append(prop)

        properties_to_mortgage.sort(key=lambda x: x["price"])

        potential_cash = 0
        final_properties = []

        for prop in properties_to_mortgage:
            potential_cash += prop["price"] / 2
            final_properties.append(prop)
            if potential_cash >= required_amount:
                break

        return final_properties if potential_cash >= required_amount else []

    def consider_trade_offer(
        self,
        ai_player,
        offered_properties,
        requested_properties,
        cash_difference,
        board_properties,
    ):
        offered_value = sum(prop["price"] for prop in offered_properties)

        for prop in offered_properties:
            if prop.get("group"):
                owned_in_group = sum(
                    1
                    for p in board_properties
                    if p.get("group") == prop.get("group")
                    and p.get("owner") == ai_player["name"]
                )
                total_in_group = sum(
                    1 for p in board_properties if p.get("group") == prop.get("group")
                )
                if owned_in_group + 1 == total_in_group:
                    offered_value += prop["price"]

        requested_value = sum(prop["price"] for prop in requested_properties)

        for prop in requested_properties:
            if prop.get("group"):
                if self.check_group_ownership(
                    prop.get("group"), board_properties, ai_player["name"]
                ):
                    requested_value *= 1.5

        total_value_difference = (offered_value + cash_difference) - requested_value

        return total_value_difference > 0 and random.random() < 0.8

    def get_property_value(self, property_data, owned_properties, total_money):
        print("\n=== AI Property Valuation Debug ===")
        print(f"DEBUG: Evaluating value of {property_data['name']}")

        base_value = property_data["price"]
        value_multiplier = 1.0

        if "group" in property_data:
            owned_in_group = sum(
                1 for p in owned_properties if p.get("group") == property_data["group"]
            )
            total_in_group = property_data.get("group_size", 3)
            print(f"DEBUG: Color group: {property_data['group']}")
            print(f"DEBUG: Owned in group: {owned_in_group}/{total_in_group}")

            if owned_in_group > 0:
                value_multiplier += 0.3 * (owned_in_group / total_in_group)
                print(
                    f"DEBUG: Group ownership bonus applied: {0.3 * (owned_in_group / total_in_group)}"
                )

        if "Station" in property_data["name"]:
            owned_stations = sum(
                1 for p in owned_properties if "Station" in p.get("name", "")
            )
            value_multiplier += 0.25 * owned_stations
            print(f"DEBUG: Owned stations: {owned_stations}")
            print(f"DEBUG: Station bonus applied: {0.25 * owned_stations}")

        elif property_data["name"] in ["Tesla Power Co", "Edison Water"]:
            owned_utilities = sum(
                1
                for p in owned_properties
                if p.get("name") in ["Tesla Power Co", "Edison Water"]
            )
            if owned_utilities > 0:
                value_multiplier += 0.5
                print(f"DEBUG: Utility bonus applied: 0.5")

        value_multiplier *= self.strategy["easy"]["max_bid_multiplier"]
        final_value = base_value * value_multiplier

        print(f"DEBUG: Base value: £{base_value}")
        print(f"DEBUG: Final multiplier: {value_multiplier}")
        print(f"DEBUG: Final calculated value: £{final_value}")

        return final_value

    def should_buy_property(self, property_data, player_money, owned_properties):
        print("\n=== AI Purchase Decision Debug ===")
        print(f"DEBUG: Evaluating purchase of {property_data['name']}")
        print(f"DEBUG: Property price: £{property_data['price']}")
        print(f"DEBUG: AI money available: £{player_money}")
        print(
            f"DEBUG: Currently owned properties: {[p.get('name', 'Unknown') for p in owned_properties]}"
        )

        if player_money < property_data["price"]:
            print("DEBUG: AI cannot afford property")
            return False

        property_value = self.get_property_value(
            property_data, owned_properties, player_money
        )
        print(f"DEBUG: Calculated property value: £{property_value}")
        print(
            f"DEBUG: Decision: {'Buy' if property_value >= property_data['price'] else 'Pass'}"
        )

        return (
            player_money >= property_data["price"]
            and property_value >= property_data["price"]
        )

    def make_auction_bid(
        self, property_data, current_bid, player_money, owned_properties
    ):
        print("\n=== AI Auction Bid Debug ===")
        print(f"DEBUG: AI evaluating bid for {property_data['name']}")
        print(f"DEBUG: Current bid: £{current_bid}")
        print(f"DEBUG: AI money available: £{player_money}")

        if player_money <= current_bid:
            print("DEBUG: AI cannot afford current bid")
            return None

        property_value = self.get_property_value(
            property_data, owned_properties, player_money
        )
        print(f"DEBUG: Calculated property value: £{property_value}")

        max_bid = min(player_money * 0.7, property_value * 1.1)
        print(f"DEBUG: Maximum bid calculated: £{max_bid}")

        if current_bid >= max_bid:
            print("DEBUG: Maximum bid too low - passing")
            return None

        bid_increment = 10
        final_bid = min(current_bid + bid_increment, max_bid)
        print(f"DEBUG: Final bid decision: £{final_bid}")

        return final_bid

    def should_develop_property(self, property_data, player_money, owned_properties):
        print("\n=== AI Development Decision Debug ===")
        print(
            f"DEBUG: Evaluating development for {property_data.name if hasattr(property_data, 'name') else 'Unknown'}"
        )
        print(f"DEBUG: AI money available: £{player_money}")

        if not property_data or not hasattr(property_data, "price"):
            print("DEBUG: Invalid property data")
            return False

        development_cost = property_data.price / 2
        print(f"DEBUG: Development cost: £{development_cost}")

        if development_cost >= player_money / 2:
            print("DEBUG: Development cost too high relative to available funds")
            return False

        money_threshold = self.strategy["easy"]["development_threshold"] * player_money
        print(f"DEBUG: Money threshold for development: £{money_threshold}")

        potential_rent = property_data.calculate_rent() * 2
        print(f"DEBUG: Potential rent after development: £{potential_rent}")

        should_develop = (
            development_cost <= money_threshold
            and potential_rent >= development_cost * 0.2 * 2
        )

        print(f"DEBUG: Development decision: {'Develop' if should_develop else 'Skip'}")
        return should_develop

    def should_mortgage_property(self, property_data, player_money):
        print("\n=== AI Mortgage Decision Debug ===")
        print(
            f"DEBUG: Evaluating mortgage for {property_data.name if hasattr(property_data, 'name') else 'Unknown'}"
        )
        print(f"DEBUG: AI money available: £{player_money}")

        if not property_data or not hasattr(property_data, "price"):
            print("DEBUG: Invalid property data")
            return False

        mortgage_threshold = self.strategy["easy"]["mortgage_threshold"] * 1500
        print(f"DEBUG: Mortgage threshold: £{mortgage_threshold}")

        should_mortgage = player_money < mortgage_threshold
        print(f"DEBUG: Mortgage decision: {'Mortgage' if should_mortgage else 'Keep'}")

        return should_mortgage

    def should_unmortgage_property(self, property_data, player_money):
        print("\n=== AI Unmortgage Decision Debug ===")
        print(
            f"DEBUG: Evaluating unmortgage for {property_data.name if hasattr(property_data, 'name') else 'Unknown'}"
        )
        print(f"DEBUG: AI money available: £{player_money}")

        if not property_data or not hasattr(property_data, "price"):
            print("DEBUG: Invalid property data")
            return False

        unmortgage_cost = property_data.price * 0.55
        print(f"DEBUG: Unmortgage cost: £{unmortgage_cost}")

        money_threshold = player_money * 0.3
        print(f"DEBUG: Money threshold for unmortgage: £{money_threshold}")

        should_unmortgage = unmortgage_cost < money_threshold
        print(
            f"DEBUG: Unmortgage decision: {'Unmortgage' if should_unmortgage else 'Keep mortgaged'}"
        )

        return should_unmortgage

    def should_sell_houses(self, property_data, player_money, target_amount):
        print("\n=== AI House Selling Decision Debug ===")
        print(
            f"DEBUG: Evaluating house selling for {property_data.name if hasattr(property_data, 'name') else 'Unknown'}"
        )
        print(f"DEBUG: AI money available: £{player_money}")
        print(f"DEBUG: Target amount needed: £{target_amount}")

        if (
            not property_data
            or not hasattr(property_data, "houses")
            or property_data.houses <= 0
        ):
            print("DEBUG: No houses to sell")
            return False

        print(f"DEBUG: Current houses on property: {property_data.houses}")

        sell_threshold = target_amount * 1.2
        print(f"DEBUG: Sell threshold: £{sell_threshold}")

        should_sell = player_money < sell_threshold
        print(f"DEBUG: House selling decision: {'Sell' if should_sell else 'Keep'}")

        return should_sell

    def get_development_priority(self, properties):
        priorities = []
        for prop in properties:
            if prop.get("group"):
                rent_to_cost_ratio = max(prop.get("house_rents", [0])) / prop.get(
                    "house_cost", float("inf")
                )
                group_completion = 1.0
                priority_score = rent_to_cost_ratio * group_completion
                priorities.append((prop, priority_score))

        return sorted(priorities, key=lambda x: x[1], reverse=True)


class HardAIPlayer:
    def __init__(self):
        self.difficulty = "hard"
        self.mood_modifier = 0.0
        self.easy_ai = EasyAIPlayer()
        print("HardAIPlayer initialized with emotion system")

    def update_mood(self, is_happy):

        if is_happy:
            self.mood_modifier = max(-0.3, self.mood_modifier - 0.05)
            print(f"DEBUG: AI is happier! Mood modifier: {self.mood_modifier}")
        else:
            self.mood_modifier = min(0.3, self.mood_modifier + 0.05)
            print(f"DEBUG: AI is angrier! Mood modifier: {self.mood_modifier}")

    def get_adjusted_probability(self, base_probability):
        # Amplified mood effect on probability adjustments (1.5x more impact)
        adjusted = base_probability + (self.mood_modifier * 1.5)
        return max(0.0, min(1.0, adjusted))

    def get_property_value(self, property_data, ai_player, board_properties):
        print("\n=== HARD AI Property Value Calculation Debug ===")
        print(
            f"DEBUG: Hard AI evaluating property: {property_data.name if hasattr(property_data, 'name') else 'Unknown'}"
        )
        print(f"DEBUG: Current mood modifier: {self.mood_modifier}")

        base_value = self.easy_ai.get_property_value(
            property_data, ai_player, board_properties
        )

        mood_multiplier = 1.0 + (self.mood_modifier * 2.0)
        final_value = base_value * mood_multiplier

        print(f"DEBUG: Base value: £{base_value}")
        print(f"DEBUG: Amplified mood multiplier: {mood_multiplier}")
        print(f"DEBUG: Final value: £{final_value}")
        return final_value

    def get_auction_bid(
        self, current_minimum, property_data, ai_player, board_properties
    ):
        print("\n=== HARD AI Auction Bid Logic Debug ===")
        print(
            f"DEBUG: Hard AI evaluating bid for: {property_data['name'] if isinstance(property_data, dict) and 'name' in property_data else 'Unknown'}"
        )
        print(f"DEBUG: Current minimum bid: £{current_minimum}")
        print(f"DEBUG: Current mood modifier: {self.mood_modifier}")

        base_bid = self.easy_ai.get_auction_bid(
            current_minimum, property_data, ai_player, board_properties
        )

        if base_bid is None:
            angry_bid_chance = self.get_adjusted_probability(0.0)
            print(f"DEBUG: Chance to bid anyway: {angry_bid_chance}")

            if random.random() < angry_bid_chance:
                perceived_value = self.get_property_value(
                    property_data, ai_player, board_properties
                )
                bid = current_minimum + random.randint(
                    10, 50 + int(100 * max(0, self.mood_modifier))
                )
                bid = min(
                    bid, ai_player.money * (0.7 + max(0, self.mood_modifier * 0.2))
                )
                print(f"DEBUG: Emotion triggered bid: £{bid}")
                return bid
            return None

        mood_multiplier = 1.0 + (self.mood_modifier * 1.5)
        final_bid = int(base_bid * mood_multiplier)

        max_percentage = 0.9 + max(0, self.mood_modifier * 0.1)
        final_bid = min(final_bid, int(ai_player.money * max_percentage))

        print(f"DEBUG: Base bid: £{base_bid}")
        print(f"DEBUG: Amplified mood multiplier: {mood_multiplier}")
        print(f"DEBUG: Final bid: £{final_bid}")
        return final_bid

    def handle_jail_strategy(self, ai_player, jail_free_cards):
        print("\n=== HARD AI Jail Strategy Debug ===")
        print(f"DEBUG: Hard AI evaluating jail strategy")
        print(f"DEBUG: Current mood modifier: {self.mood_modifier}")

        if not ai_player.get("in_jail", False):
            print(f"DEBUG: Not in jail - no action needed")
            return None

        base_strategy = self.easy_ai.handle_jail_strategy(ai_player, jail_free_cards)

        if base_strategy == "roll_doubles" and ai_player["money"] >= 50:
            pay_chance = self.get_adjusted_probability(0.5)
            print(f"DEBUG: Chance to pay fine: {pay_chance}")

            if random.random() < pay_chance:
                print(f"DEBUG: Emotion triggered decision to pay fine")
                return "pay_fine"

        print(f"DEBUG: Using strategy: {base_strategy}")
        return base_strategy

    def should_mortgage_property(self, ai_player, required_money):
        print("\n=== HARD AI Mortgage Strategy Debug ===")
        print(f"DEBUG: Hard AI evaluating mortgage strategy")
        print(f"DEBUG: Required money: £{required_money}")
        print(f"DEBUG: Current mood modifier: {self.mood_modifier}")

        return self.easy_ai.should_mortgage_property(ai_player, required_money)

    def handle_property_development(self, ai_player, board_properties):
        print("\n=== HARD AI Development Strategy Debug ===")
        print(f"DEBUG: Hard AI evaluating development strategy")
        print(f"DEBUG: Current mood modifier: {self.mood_modifier}")

        base_result = self.easy_ai.handle_property_development(
            ai_player, board_properties
        )

        if not base_result:
            money_threshold = 200 - (self.mood_modifier * 100)
            if ai_player["money"] >= money_threshold:
                develop_chance = self.get_adjusted_probability(0.3)

                if random.random() < develop_chance:
                    player_properties = []
                    for prop_key, prop in board_properties.items():
                        if (
                            isinstance(prop, dict)
                            and prop.get("owner") == ai_player["name"]
                        ):
                            player_properties.append(prop)
                        elif hasattr(prop, "owner") and prop.owner == ai_player["name"]:
                            player_properties.append(prop)

                    for prop in player_properties:
                        if hasattr(
                            prop, "group"
                        ) and self.easy_ai.check_group_ownership(
                            prop.group, board_properties, ai_player["name"]
                        ):
                            money_reserve = 0.3 - (self.mood_modifier * 0.1)
                            house_cost = prop.price / 2
                            money_after_purchase = ai_player["money"] - house_cost
                            minimum_reserve = ai_player["money"] * money_reserve

                            if money_after_purchase >= minimum_reserve:
                                return prop

        return base_result

    def should_buy_property(self, property_data, player_money, owned_properties):
        print("\n=== HARD AI Purchase Decision Debug ===")
        print(f"DEBUG: Hard AI evaluating purchase of {property_data['name']}")
        print(f"DEBUG: Property price: £{property_data['price']}")
        print(f"DEBUG: AI money available: £{player_money}")
        print(f"DEBUG: Current mood modifier: {self.mood_modifier}")

        base_decision = self.easy_ai.should_buy_property(
            property_data, player_money, owned_properties
        )

        if not base_decision and player_money >= property_data["price"]:
            buy_chance = self.get_adjusted_probability(0.2)
            print(f"DEBUG: Chance to buy anyway: {buy_chance}")

            max_price_ratio = 0.7 + (self.mood_modifier * 0.2)
            can_afford = player_money * max_price_ratio >= property_data["price"]

            if can_afford and random.random() < buy_chance:
                print(f"DEBUG: Emotion triggered decision to buy property")
                print(f"DEBUG: Max price ratio: {max_price_ratio}")
                return True

        elif base_decision and self.mood_modifier < 0:
            pass_chance = -self.mood_modifier * 1.5
            print(f"DEBUG: Amplified chance to pass: {pass_chance}")

            if random.random() < pass_chance:
                print(f"DEBUG: Emotion triggered decision to pass on property")
                return False

        print(f"DEBUG: Final decision: {'Buy' if base_decision else 'Pass'}")
        return base_decision
