#!/usr/bin/env python3
"""
Assignment 2 - Sleeping Coders
CSSE1001/7030
Semester 2, 2019
"""

import random

__author__ = "Student name:Ziliang WANG & Student number:45236499"


# Write your classes here

class Card:
    """
        A class to manage the card's actions.
    """
    def play(self, player, game):
        """
            player played card, remove that card in player's hand_card
            after remove a card(player played a card), player hand_cards add a card from first card from the pickup pile
            CodersGame's action set to 'NO_ACTION'
        """
        player.hand_cards.get_cards().remove(self)
        player.hand_cards.get_cards().append(game.pick_card()[0])
        game.set_action('NO_ACTION')

    def action(self, player, game, slot):
        """
           special card function will be in special card's class
        """
        pass

    def __str__(self):
        """
            return Card()(str)
        """
        return 'Card()'

    def __repr__(self):
        """
            return Card()(str)
        """
        return 'Card()'


class NumberCard(Card):
    """" A class that contains NumberCard actions"""

    def __init__(self, number):
        """
            Construct a new number ,number card has an associated number value
        """
        self._number = number

    def __str__(self):
        return 'NumberCard({})'.format(self._number)

    def __repr__(self):
        return 'NumberCard({})'.format(self._number)

    def get_number(self):
        """
             Returns the card number.
        """
        return self._number

    def play(self, player, game):
        """
            player played card, remove that card in player's hand_card
            after remove a card(player played a card), player hand_cards add a card from first card from the pickup pile
            CodersGame's action set to 'NO_ACTION'
        """
        player.hand_cards.get_cards().remove(self)
        player.hand_cards.add_card(game.pick_card()[0])
        game.set_action('NO_ACTION')
        game.next_player()

class CoderCard(Card):
    """" A class that contains CoderCard actions"""

    def __init__(self, coder):
        """
            Construct a new coder stores the name of a coder card.
        """
        self._coder = coder

    def __str__(self):
        return 'CoderCard({})'.format(self._coder)

    def __repr__(self):
        return 'CoderCard({})'.format(self._coder)

    def get_name(self):
        """
             Returns the card name.
        """
        return self._coder

    def play(self,player,game):
        """
            CodersGame's action set to 'NO_ACTION'
        """
        game.set_action("NO_ACTION")

class TutorCard(Card):
    """" A class that contains TutorCard actions"""

    def __init__(self, tutor):
        """
            Construct a new coder  stores the name of a tutor card , tutor card can be played by a player to pickup a coder card.
        """
        self._tutor = tutor

    def __repr__(self):
        return 'TutorCard({})'.format(self._tutor)

    def __str__(self):
        return 'TutorCard({})'.format(self._tutor)

    def get_name(self):
        """
            Returns the tutor_card's name.
        """
        return self._tutor

    def play(self, player, game):
        """
            player played card, remove that card in player's hand_card
            after remove a card(player played a card), player hand_cards add a card from first card from the pickup pile
            CodersGame's action set to 'PICKUP_CODER'

            Parameters:
                player(Player): The selecting player
                game(CodersGame): CodersGame
        """
        player.hand_cards.get_cards().remove(self)
        player.hand_cards.get_cards().append(game.pick_card()[0])
        game.set_action('PICKUP_CODER')

    def action(self, player, game, slot):
        """
            take sleeping_coder card from sleeping_coders pile
            add to player's coder pile
            delete picked card from sleeping_coders pile
            CodersGame's action set to 'NO_ACTION'

            Parameters:
                player(Player): The selecting player
                game(CodersGame): CodersGame
                slot(int): the slot of sleeping_coders pile
        """
        coder_card = game.get_sleeping_coder(slot)

        player.coder_cards.add_card(coder_card)

        game.set_sleeping_coder(slot, None)

        game.set_action("NO_ACTION")

        game.next_player()


class KeyboardKidnapperCard(Card):
    """" A class that contains KeyboardKidnapperCard actions"""

    def __init__(self):
        """
        """
        pass

    def __str__(self):

        return 'KeyboardKidnapperCard()'

    def __repr__(self):
        return 'KeyboardKidnapperCard()'

    def play(self, player, game):
        """
            delete played card
            add a new card from the pickup pile in the game.
            CodersGame's action set to 'STEAL_CODER'
        Parameters:
            player(Player): The selecting player
            game(CodersGame): CodersGame
        """
        player.hand_cards.get_cards().remove(self)
        player.hand_cards.add_card(game.pick_card()[0])
        game.set_action('STEAL_CODER')

    def action(self, player, game, slot):
        """
            take wakened card from sleeping_coders pile
            player who use kidnapper card
            add steal card into coder pile
            delete picked card
            CodersGame's action set to 'NO_ACTION' order for next player
            turns to next player

        Parameters:
            player(Player):  player refers to the player to which the coder belongs to.
            game(CodersGame): CodersGame
            slot(int): the slot of sleeping_coders pile
        """
        codercard = player.get_coders().get_card(slot)  

        kidnapper = game.current_player()  

        kidnapper.coder_cards.get_cards().append(codercard)  

        player.coder_cards.get_cards().pop(slot)  

        game.set_action("NO_ACTION")

        game.next_player()  


class AllNighterCard(Card):
    """" A class that contain AllNighterCard actions"""

    def __init__(self):
        """
        """
        pass

    def __str__(self):
        return 'AllNighterCard()'

    def __repr__(self):
        return 'AllNighterCard()'

    def play(self, player, game):
        """
            remove played card
            add first card from the pickup pile
            card into hand_cards
            CodersGame's action to 'SLEEP_CODER'
        Parameters:
            player(Player):The selecting player.
            game(CodersGame): CodersGame
        """
        player.hand_cards.get_cards().remove(self)
        player.hand_cards.add_card(game.pick_card()[0])
        game.set_action('SLEEP_CODER')

    def action(self, player, game, slot):
        """
            order to delete card
            delete from player coder_cards
            a empty index in sleeping_coders pile
            put card back to sleeping_coders pile
            CodersGame's action set to 'NO_ACTION' order for next player
            turns to next player

        Parameters:
            player(Player):  player refers to the player to which the coder belongs to.
            game(CodersGame): CodersGame
            slot(int): the slot of sleeping_coders pile
        """
        codercard = player.coder_cards.get_card(slot)
        
        player.coder_cards.remove_card(slot)

        spare = game.get_sleeping_coders().index(None)

        game.set_sleeping_coder(spare, codercard)

        game.set_action("NO_ACTION")

        game.next_player()


class Deck:
    """" A class that contains management of cards actions"""
    def __init__(self, starting_cards=None):
        """
            Construct a cards list , if starting_cards is none give cards as a new list with empty,
            if starting_cards is not NONE, then give the value of starting_cards to new cards
        """

        if starting_cards == None:
            self.cards = []
        else:
            self.cards = starting_cards

    def get_cards(self):
        """
            (List[Card]):cardReturns a list of cards in the deck.
        """
        return self.cards

    def get_card(self, slot):
        """
            (Card):Return the card at the specified slot in a deck.
        """
        return self.cards[slot]

    def top(self):
        """
            (Card): Returns the card on the top of the deck
        """
        return self.get_card(-1)

    def remove_card(self, slot):
        """
             Removes a card at the given slot in a deck
        """
        self.cards.pop(slot)

    def get_amount(self):
        """
             Returns the amount of cards in a deck
        """
        return len(self.cards)

    def shuffle(self):
        """
            Shuffles the order of the cards in the deck.
        """
        random.shuffle(self.cards)

    def pick(self, amount=1):
        """
            (List[Card]):Takes the first 'amount' of cards off the deck and returns them.
        """
        card = []
        for i in range(amount):
            card.append(self.top())
            self.remove_card(-1)
        return card

    def add_card(self, card):
        """
            Places a card on top of the deck.

            Parameters:
                card(Card): the card order add to get_cards()
        """
        self.cards.append(card)

    def add_cards(self, cards):
        """
            Places a card list  on top of the deck.

        Parameters:
            cards(List[Card]): the card list order add to get_cards()
        """
        self.cards += cards

    def copy(self, other_deck):
        """
            Copies all of the cards from the other_deck parameter into the current deck, extending the list of cards of the current deck.

        Parameters:
            other_deck(other_deck): another player's deck
        """
        self.add_cards(other_deck.cards)

    def __str__(self):
        """
            Returns the string representation of the deck
        """
        out = 'Deck('
        if self.cards == []:
            out += ")"
        else:
            for card in self.cards:
                out += str(card)
                out += ", "
            out = out[:-2]
            out += ")"
        return out

    def __repr__(self):
        """
            Returns the string representation of the deck
        """
        out = 'Deck('
        if self.cards == []:
            out += ")"
        else:
            for card in self.cards:
                out += str(card)
                out += ", "
            out = out[:-2]
            out += ")"
        return out


class Player:
    """ A class to manage information of player in the game """

    def __init__(self, name):
        """
            Construct a new player represents one of the players in the game.


        Parameters:
            name(str): name of the player.
        """
        self.name = name
        self.hand_cards = Deck()
        self.coder_cards = Deck()

    def get_name(self):
        """
            Returns the name of the player.
        """
        return self.name

    def get_hand(self):
        """
             Returns the players deck of cards.
        """
        return self.hand_cards

    def get_coders(self):
        """"
            Returns the players deck of collected coder cards

        """
        return self.coder_cards

    def has_won(self):
        """
            Returns True if and only if the player has 4 or more coders
        """
        if self.coder_cards.get_amount() >= 4:
            return True
        else:
            return False

    def __str__(self):
        """
            Returns the string representation of the player
        """
        return "Player({}, {}, {})".format(self.name, str(self.hand_cards), str(self.coder_cards))

    def __repr__(self):
        """
            Returns the string representation of the player
        """
        return "Player({}, {}, {})".format(self.name, str(self.hand_cards), str(self.coder_cards))


def main():
    print("Please run gui.py instead")


if __name__ == "__main__":
    main()


