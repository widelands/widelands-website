import math
from .models import Game, Participant, Player_Rating, Temporary_user, Season
from decimal import getcontext, Decimal
from datetime import datetime, timedelta

import pprint #Temporary

#############
# constants #
#############
STARTING_SCORE = Decimal(1500).quantize(Decimal('1.00'))
STANDARD_DEVIATION = Decimal(300).quantize(Decimal('1.00'))
VOLATILITY = Decimal(0.06).quantize(Decimal('1.00000'))
VOLATILITY_CHANGE = 0.2
EPISLON = 0.000001


class Glicko_rating ():
    def __init__ (self):
        self.starting_score = STARTING_SCORE
        self.standard_deviation = STANDARD_DEVIATION
        self.volatility = VOLATILITY
        self.volatility_change = VOLATILITY_CHANGE
        self.epsilon = EPISLON

    def evaluate_new_score(self):
        #self.create_test_date()
        games = self.get_games_played()
        for g in games:
            print (g.start_date)
        data = self.get_temp_data(games)
        pprint.pprint(data, width=1)
        for player in data:
            print (player['username'])

            ## Step 3
            μ = player['score']
            φ = player['deviation']
            
            a = 0
            
            for game in player['games']:
                
                E = self.stp3_E(μ, game['competitor']['score'], game['competitor']['deviation'])
                print ('E:', E)
                g = self.stp3_g(game['competitor']['deviation'])
                a += g**Decimal(2)*E*(Decimal(1)-E)
            v = a**Decimal(-1)

            ## Step 4
            a = 0
            for game in player['games']:
                E = self.stp3_E(μ, game['competitor']['score'], game['competitor']['deviation'])
                a += self.stp3_g(game['competitor']['deviation'])*(game['winner'] - E)
            delta = v * a
            print ('Yohoha: ', delta, v, a)

            ## Step 5
            σ = player['volatility']
            #new_σ = self.stp5_σ(delta, φ, v, σ)

            ## Step 6
            middle_φ = (φ**Decimal(2) + σ**Decimal(2))**Decimal(0.5)

            ## Step 7
            final_φ = Decimal(1)/((Decimal(1)/middle_φ**2)+ (Decimal(1)/v))**Decimal(0.5)

            a = 0
            for game in player['games']:
                E = self.stp3_E(μ, game['competitor']['score'], game['competitor']['deviation'])
                a += self.stp3_g(game['competitor']['deviation']) * (game['winner'] - E)
            final_μ = μ + final_φ**2 * a

            print ('Yohoho: ', final_φ, final_μ)
            
            ## Step 8
            tu = Temporary_user.objects.get(
                username = player['username']
            )

            pr = Player_Rating.objects.filter().get(
                user = tu,
                rating_type= 3
            )
            pr.decimal1 = self.stp8_rating(final_μ)
            pr.decimal2 = self.stp8_deviation(final_φ)
            pr.decimal3 = self.volatility
            pr.save()


    def stp2_rating(self, r):
        μ = (Decimal(r) - Decimal(1500))/Decimal(173.7178)
        return μ

    def stp2_deviation(self, RD):
        φ = Decimal(RD)/Decimal(173.7178)
        return φ

    def stp8_rating(self, μ):
        r = Decimal(173.7178) * μ + Decimal(1500)
        return r
    
    def stp8_deviation(self, φ):
        RD = Decimal(173.7178) * φ
        return RD

    def stp3_E(self, μ, μj, φj):
        a = -self.stp3_g(φj)*(μ - μj)
        b = Decimal(math.exp(a))
        E = Decimal(1)/(Decimal(1) + b)
        return E

    def stp3_g(self, φ):
        a = Decimal(3 * φ**2)
        b = Decimal(math.pi**2)
        g = 1 / ((1 + a/b))**Decimal(0.5)
        return g

    def function_f(self, x, Delta, φ, v, σ):
        numerator1 = Delta**Decimal(2) - φ**Decimal(2) - v - Decimal(math.exp(x))
        numerator1 *= Decimal(math.exp(x))
        denominator1 = φ**Decimal(2) + v + Decimal(math.exp(x))
        denominator1 = denominator1 ** Decimal(2)
        denominator1 *= Decimal(2)

        a = Decimal(2)*Decimal(math.log(σ))
        numerator2 = x - a
        denominator2 = Decimal(self.volatility_change)**Decimal(2)

        result = numerator1 / denominator1
        result -= numerator2 / denominator2
        return result

    def stp5_σ(self, Delta, φ, v, σ):
        ε = self.epsilon
        a = Decimal(2)*Decimal(math.log(σ))
        A = a

        if Delta**Decimal(2) > φ**Decimal(2) + v:
            B = math.log(Delta**Decimal(2) - φ**Decimal(2) - v)
        else:
            k = Decimal(1)
            while self.function_f(a - Decimal(k)*Decimal(self.volatility_change), Delta, φ, v, σ):
                k += Decimal(1)
            B = a - k*self.volatility_change

        f_A = self.function_f(A, Delta, φ, v, σ)
        f_B = self.function_f(B, Delta, φ, v, σ)

        while abs(B-A) > ε:
            proportion = f_A / (f_B - f_A)  
            C = A + (A - B) * proportion
            f_C = self.function_f(C, Delta, φ, v, σ)

            if f_C*f_B < Decimal(0):
                A = B
                f_A = f_B
            else:
                f_A /= Decimal(2)

            B = C
            f_B = f_C

        sigma_prim = math.exp(A / Decimal(2))
        return sigma_prim


    def get_games_played(self):
        games = []

        s = Season.objects.get(
            name = 'Season I: The season of many builds'
        )

        end_date = datetime.now()
        delta = end_date - s.start_date 


        # calculate Glicko score
        for i in range(delta.days):
            if i % 30 == 0:
                rating_day = s.start_date + timedelta(days=i)
                for g in Game.objects.order_by('start_date'):
                    date_is_in_range = rating_day - timedelta(days = 30) <= g.start_date <= rating_day
                    game_is_in_season = s.start_date <= g.start_date <= s.end_date
                    if date_is_in_range and game_is_in_season:
                        games.append(g)

        return games

    #step1
    # get data of all the player that will be evaluated on this period
    # Then sanitize the data for use in glicko
    # combined in one function to reduce calls to db
    def get_data(self, games):
        data = []
        for tu in Temporary_user.objects.all():
            player_data = {}
            player_data['username'] = tu.username
            try:
                pr = Player_Rating.objects.get(user=tu, rating_type= 3)
            except Player_Rating.DoesNotExist:
                pr = Player_Rating.objects.create(
                    user=tu, 
                    rating_type= 3,
                    decimal1 = self.starting_score,
                    decimal2 = self.standard_deviation,
                    decimal3 = self.volatility,
                )
                pr.save()
            player_data['score'] = self.stp2_rating(pr.decimal1)
            player_data['deviation'] = self.stp2_deviation(pr.decimal2)
            player_data['volatility'] = pr.decimal3
            clean_games = []
            for g in Game.objects.all():
                game_data = {}
                participated_in_game = False
                for p in Participant.objects.filter(game = g):
                    if p.user == tu:
                        participated_in_game = True
                if participated_in_game:
                    for p in Participant.objects.filter(game = g):
                        if p.user == tu:
                            game_data['winner'] = 1 if p.team == g.win_team else 0 #To change after understanding where bug in view.py
                        else:
                            try:
                                pr = Player_Rating.objects.get(user=p.user, rating_type= 3)
                            except Player_Rating.DoesNotExist:
                                print ('PROBLEM')
                            game_data['competitor'] = {}
                            game_data['competitor']['score'] = self.stp2_rating(pr.decimal1)
                            game_data['competitor']['deviation'] = self.stp2_deviation(pr.decimal2)
                            game_data['competitor']['volatility'] = pr.decimal3
                        
                    clean_games.append(game_data)
            player_data['games'] = clean_games
            data.append(player_data)
        return data

    def get_temp_data(self, games):
        data = []
        for tu in Temporary_user.objects.all():
            player_data = {}
            player_data['username'] = tu.username
            try:
                pr = Player_Rating.objects.get(user=tu, rating_type= 3)
            except Player_Rating.DoesNotExist:
                print ('PROBLEM')
            player_data['score'] = self.stp2_rating(pr.decimal1)
            player_data['deviation'] = self.stp2_deviation(pr.decimal2)
            player_data['volatility'] = pr.decimal3
            clean_games = []
            for g in Game.objects.all():
                game_data = {}
                participated_in_game = False
                for p in Participant.objects.filter(game = g):
                    if p.user == tu:
                        participated_in_game = True
                if participated_in_game:
                    for p in Participant.objects.filter(game = g):
                        if p.user == tu:
                            game_data['winner'] = 1 if p.team == g.win_team else 0 #To change after understanding where bug in view.py
                        else:
                            try:
                                pr = Player_Rating.objects.get(user=p.user, rating_type= 3)
                            except Player_Rating.DoesNotExist:
                                print ('PROBLEM')
                            game_data['competitor'] = {}
                            game_data['competitor']['score'] = self.stp2_rating(pr.decimal1)
                            game_data['competitor']['deviation'] = self.stp2_deviation(pr.decimal2)
                            game_data['competitor']['volatility'] = pr.decimal3
                        
                    clean_games.append(game_data)
            player_data['games'] = clean_games
            data.append(player_data)
        return data

    def create_test_date(self):
        s, created = Season.objects.get_or_create(
            start_date= '2019-06-01',
            end_date='2019-12-01',
            name='Season I: The season of many builds'
        )
        s.save()

        g1, c1 = Game.objects.get_or_create(
            start_date = '2019-08-08',
            game_type = 1,
            game_map = 'Crater',
            win_team = 1,
            game_status = 1, #todo when working on user submissions
            game_breaks = 0, #todo when working on user submissions
        )
        if c1:
            g1.save()

        g2, c2 = Game.objects.get_or_create(
            start_date = '2019-08-08',
            game_type = 1,
            game_map = 'Ice war',
            win_team = 1,
            game_status = 1, #todo when working on user submissions
            game_breaks = 0, #todo when working on user submissions
        )
        if c2:
            g2.save()

        g3, c3 = Game.objects.get_or_create(
            start_date = '2019-08-08',
            game_type = 1,
            game_map = 'Sea',
            win_team = 1,
            game_status = 1, #todo when working on user submissions
            game_breaks = 0, #todo when working on user submissions
        )
        if c3:
            g3.save()

        tu1, c4 = Temporary_user.objects.get_or_create(
            username = 'main_player'
        )
        if c4:
            tu1.save()
        tu2, c5 = Temporary_user.objects.get_or_create(
            username = 'looser'
        )
        if c5:
            tu2.save()
        tu3, c6 = Temporary_user.objects.get_or_create(
            username = 'winner1'
        )
        if c6:
            tu3.save()
        tu4, c7 = Temporary_user.objects.get_or_create(
            username = 'winner2'
        )
        if c7:
            tu4.save()

        p1, c8 = Participant.objects.get_or_create(
            user = tu1,
            game = g1,
            team = 1,
            submitter = False,
            tribe = 1,
        )
        p2, c9 = Participant.objects.get_or_create(
            user = tu2,
            game = g1,
            team = 0,
            submitter = False,
            tribe = 1,
        )
        p3, c10 = Participant.objects.get_or_create(
            user = tu1,
            game = g2,
            team = 0,
            submitter = False,
            tribe = 1,
        )
        p4, c11 = Participant.objects.get_or_create(
            user = tu3,
            game = g2,
            team = 1,
            submitter = False,
            tribe = 1,
        )
        p5, c12 = Participant.objects.get_or_create(
            user = tu1,
            game = g3,
            team = 0,
            submitter = False,
            tribe = 1,
        )
        p6, c13 = Participant.objects.get_or_create(
            user = tu4,
            game = g3,
            team = 1,
            submitter = False,
            tribe = 1,
        )
        if c8:
            p1.save()
        if c9:
            p2.save()
        if c10:
            p3.save()
        if c11:
            p4.save()
        if c12:
            p5.save()
        if c13:
            p6.save()
        pr1, c14 = Player_Rating.objects.get_or_create(
            user = tu1,
            rating_type= 3,
            decimal1 = 1500,
            decimal2 = 200,
            decimal3 = self.volatility,
            season = s,
        )
        pr2, c15 = Player_Rating.objects.get_or_create(
            user = tu2,
            rating_type= 3,
            decimal1 = 1400,
            decimal2 = 30,
            decimal3 = self.volatility,
            season = s,
        )
        pr3, c16 = Player_Rating.objects.get_or_create(
            user = tu3,
            rating_type= 3,
            decimal1 = 1550,
            decimal2 = 100,
            decimal3 = self.volatility,
            season = s,
        )
        pr4, c17 = Player_Rating.objects.get_or_create(
            user = tu4,
            rating_type= 3,
            decimal1 = 1700,
            decimal2 = 300,
            decimal3 = self.volatility,
            season = s,
        )
        if c14:
            pr1.save()
        if c15:
            pr2.save()
        if c16:
            pr3.save()
        if c17:
            pr4.save()