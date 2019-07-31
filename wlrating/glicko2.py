import math
from .models import Rating
from decimal import getcontext, Decimal


#############
# constants #
#############
STARTING_SCORE = Decimal(1500).quantize(Decimal('1.00'))
STANDARD_DEVIATION = Decimal(300).quantize(Decimal('1.00'))
VOLATILITY = Decimal(0.06).quantize(Decimal('1.00000'))

VOLATILITY_CHANGE = 1.0

class Glicko_rating ():
    def __init__ (self, games_list):
        self.starting_score = STARTING_SCORE
        self.standard_deviation = STANDARD_DEVIATION
        self.volatility = VOLATILITY
        self.volatility_change = VOLATILITY_CHANGE
        self.games_list = games_list

        print (Decimal(self.standard_deviation))
    def evaluate_new_score(self):
        self.player_list = []
        self.get_players_that_played()
        self.convert_to_glicko_scale()

    #step1
    # get data of all the player that will be evaluated on this period
    def get_players_that_played(self):
        
        for g in self.games_list:
            player1_exist = False
            player2_exist = False
            player_already_in_list = False
            if player_list:
                for u in player_list:
                    if g['player1'] == u['username']:
                        player1_exist = True
                    elif g['player2'] == u['username']:
                        player2_exist = True
            if not player1_exist:
                player_data = {}
                player_data['username'] = self.starting_score
                player_data['score'] = r.rating
                player_data['standard_deviation'] = r.standard_deviation
                player_data['volatility'] = r.volatility
                player_list.append(player_data)

            if not player2_exist:
                player_data = {}
                player_data['username'] = r.player
                player_data['score'] = r.rating
                player_data['standard_deviation'] = r.standard_deviation
                player_data['volatility'] = r.volatility
                player_list.append(player_data)

            for r in Rating.objects.order_by('player'):
                if r.player == g['player1'] :
                    player1_exist = True
                    
                if r.player == g['player2']:
                    player2_exist = True
                        
                if not player1_exist:
                    r = Rating.objects.create(
                        player=g['player1'],
                        rating = self.starting_score,
                        standard_deviation = self.standard_deviation,
                        volatility = self.volatility,
                    )
                    r.save()
                if not player2_exist:
                    r = Rating.objects.create(
                        player=g['player2'],
                        rating = self.starting_score,
                        standard_deviation = self.standard_deviation,
                        volatility = self.volatility,
                    )
                    r.save()

    #step2
    def convert_to_glicko_scale(self):
        for p in self.player_list:
            print (p)

    def add_to_db(self, username):

