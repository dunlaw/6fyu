# Property Tycoon cards.py
# It contains the classes for the cards, such as the card type, the card text, and the card action.

from enum import Enum
import random
from src.Game_Logic import pot_luck_cards, opportunity_knocks_cards


class CardType(Enum):
    POT_LUCK = "pot luck"
    OPPORTUNITY_KNOCKS = "opportunity knocks"


class Card:
    def __init__(self, text, action, card_type):
        self.text = text
        self.action = action
        self.card_type = card_type
        self.requires_input = "take opportunity knocks" in text.lower()
        self.is_special = any(
            keyword in text.lower()
            for keyword in ["jail free", "advance to", "go back", "collect", "pay"]
        )


class CardDeck:
    def __init__(self, card_type):
        self.card_type = card_type
        self.cards = []
        self.discard_pile = []
        self.initialize_deck()
        self.last_drawn_card = None

    def initialize_deck(self):
        if self.card_type == CardType.POT_LUCK:
            card_data = pot_luck_cards
        else:
            card_data = opportunity_knocks_cards

        self.cards = []
        for card_info in card_data:
            card = Card(
                text=card_info["text"],
                action=card_info["action"],
                card_type=self.card_type,
            )
            self.cards.append(card)
        random.shuffle(self.cards)

    def draw_card(self):
        if not self.cards:
            if self.discard_pile:
                self.cards = self.discard_pile
                self.discard_pile = []
                random.shuffle(self.cards)
            else:
                return None

        self.last_drawn_card = self.cards.pop()
        return self.last_drawn_card

    def return_card(self, card, to_bottom=True):
        if to_bottom:
            self.discard_pile.append(card)
        else:
            self.discard_pile.insert(0, card)

    def return_jail_card(self, card_type):
        jail_card = next(
            (
                card
                for card in self.cards + self.discard_pile
                if "jail free" in card.text.lower()
            ),
            None,
        )
        if not jail_card:
            jail_card = Card(
                next(
                    c["action"]
                    for c in (
                        pot_luck_cards
                        if card_type == CardType.POT_LUCK
                        else opportunity_knocks_cards
                    )
                    if "jail free" in c["text"].lower()
                ),
                card_type,
            )
        self.return_card(jail_card, to_bottom=True)

    def peek_top_card(self):
        if not self.cards and self.discard_pile:
            self.cards = self.discard_pile
            self.discard_pile = []
            random.shuffle(self.cards)
        return self.cards[-1] if self.cards else None

    def get_remaining_count(self):
        return len(self.cards)

    def get_discard_count(self):
        return len(self.discard_pile)
