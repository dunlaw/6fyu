# Property Tycoon Property.py
# It contains the classes for the properties, such as the rent, the house costs, and the hotel costs.


class Property:
    def __init__(self, data):
        self.name = data["name"]
        self.group = data["group"]
        self.price = data.get("price", 0)
        self.base_rent = data.get("rent", 0)
        self.owner = None
        self.houses = 0
        self.has_hotel = False
        self.house_costs = data.get("house_costs", [])
        self.is_station = data.get("is_station", False)
        self.is_utility = data.get("is_utility", False)
        self.mortgaged = False

    def calculate_rent(self, dice_roll=None, properties=None):
        if self.mortgaged:
            return 0

        if self.is_station:
            if not properties:
                return self.base_rent
            station_count = sum(
                1 for p in properties if p.is_station and p.owner == self.owner
            )
            return self.base_rent * (2 ** (station_count - 1))

        elif self.is_utility:
            if not properties or not dice_roll:
                return 0
            utility_count = sum(
                1 for p in properties if p.is_utility and p.owner == self.owner
            )
            multiplier = 10 if utility_count > 1 else 4
            return dice_roll * multiplier

        else:
            if self.has_hotel:
                return self.house_costs[-1] if self.house_costs else self.base_rent * 5
            elif self.houses > 0:
                house_index = min(self.houses - 1, len(self.house_costs) - 1)
                return (
                    self.house_costs[house_index]
                    if self.house_costs
                    else self.base_rent * (self.houses + 1)
                )
            elif self.has_monopoly(properties):
                return self.base_rent * 2
            return self.base_rent

    def has_monopoly(self, properties):
        if not self.group or not properties:
            return False

        group_properties = [p for p in properties if p.group == self.group]
        return all(p.owner == self.owner for p in group_properties)

    def can_build_house(self, properties):
        if self.is_station or self.is_utility or self.mortgaged or self.has_hotel:
            return False

        if not self.has_monopoly(properties):
            return False

        if not properties:
            return False

        group_properties = [p for p in properties if p.group == self.group]
        min_houses = min(p.houses for p in group_properties)
        return self.houses <= min_houses

    def can_build_hotel(self, properties):
        if self.is_station or self.is_utility or self.mortgaged or self.has_hotel:
            return False

        if not self.has_monopoly(properties):
            return False

        if self.houses < 5:
            return False

        if not properties:
            return False

        group_properties = [p for p in properties if p.group == self.group]
        return all(p.houses >= 5 for p in group_properties)

    def build_house(self):
        if not self.has_hotel:
            self.houses += 1
            return True
        return False

    def build_hotel(self):
        if self.houses >= 5 and not self.has_hotel:
            self.houses = 0
            self.has_hotel = True
            return True
        return False

    def sell_house(self):
        if self.houses > 0:
            self.houses -= 1
            return True
        return False

    def sell_hotel(self):
        if self.has_hotel:
            self.has_hotel = False
            self.houses = 5
            return True
        return False

    def mortgage(self):
        if not self.mortgaged and self.houses == 0 and not self.has_hotel:
            self.mortgaged = True
            return True
        return False

    def unmortgage(self):
        if self.mortgaged:
            self.mortgaged = False
            return True
        return False

    def get_mortgage_value(self):
        return self.price // 2

    def get_unmortgage_cost(self):
        return int(self.get_mortgage_value() * 1.1)

    def get_house_sale_value(self):
        if not self.house_costs:
            return 0
        house_cost = self.house_costs[0]
        return house_cost // 2

    def get_hotel_sale_value(self):
        if not self.house_costs:
            return 0
        hotel_purchase_price = self.house_costs[0] * 5 if self.house_costs else 0
        return hotel_purchase_price // 2

    def charge_rent(self, player, dice_roll=None):
        if self.owner and self.owner != player:
            rent = self.calculate_rent(dice_roll, self.owner.properties)
            print(
                f"{player.name} landed on {self.name}, paying £{rent} rent to {self.owner.name}"
            )
            player.pay(rent)
            self.owner.receive(rent)
            return rent
        return 0
