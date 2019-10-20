import math
from django.contrib.auth.models import User
from .models import Game, Participant, Player_Rating, Rating_user, Season
from decimal import getcontext, Decimal
from datetime import datetime, timedelta
from django.conf import settings

class Glicko_rating ():
    def __init__ (self):
        self.starting_score = Decimal(settings.STARTING_SCORE).quantize(Decimal('1.00'))
        self.standard_deviation = Decimal(settings.STANDARD_DEVIATION).quantize(Decimal('1.00'))
        self.volatility = Decimal(settings.VOLATILITY).quantize(Decimal('1.00000'))
        self.tau = settings.TAU
        self.epsilon = settings.EPISLON
        self.iteration_limit = settings.ITERATION_LIMIT
        self.game_per_round = settings.GAME_PER_ROUND

    def calculate_all_games(self, season_name):
        games = []
        s = Season.objects.get(
            name = season_name
        )

        # Select games in season and evaluate them by groups of ten. Change db at each of these "rounds"
        total_games = 0
        games_of_season_list = []
        for g in Game.objects.order_by('start_date').filter(counted_in_score= False):
            game_is_in_season = s.start_date <= g.start_date <= s.end_date
            if game_is_in_season:
                total_games += 1
                games_of_season_list.append(g)

        round_games = 0
        games_until_last = total_games
        for g in games_of_season_list:
            if round_games < self.game_per_round:
                games.append(g)
                round_games+=1
            else:
                games.append(g)
                self.calculate_round(games, s)
                round_games = 0
                games = []
            games_until_last -= 1
            if games_until_last == 0:
                self.calculate_round(games, s)
            g.counted_in_score= True
            g.save()


    def calculate_round(self, games, s):
        # step 1 and 2
        data = self.get_data(games, s)
        for player in data:
            # step 3 to 8         
            rating, deviation, volatility = self.glicko_process(player)

            u = User.objects.get(username=player['username'])
            ru = Rating_user.objects.get(user=u)
            pr = Player_Rating.objects.get(user=ru, rating_type= 3)
            pr.decimal1 = rating
            pr.decimal2 = deviation
            pr.decimal3 = volatility
            pr.save()

            
    def glicko_process(self, player):

        ## Step 3
        mu = player['score']
        phi = player['deviation']
        sigma = player['volatility']
        nu = self.step3_nu(player['games'], mu)

        ## Step 4
        Delta = self.step4_Delta(player['games'], mu, nu)

        ## Step 5
        sigma_prime = self.step5_sigma(Delta, phi, nu, sigma)

        ## Step 6
        phi_star = self.step6_phi_star(phi, sigma_prime)

        ## Step 7
        phi_prime = self.step7_phi_prime(phi_star,nu)
        mu_prime = self.step7_mu_prime(player['games'], mu, phi_prime)

        ## Step 8
        final_score = self.step8_rating(mu_prime)
        final_deviation = self.step8_deviation(phi_prime)
        final_volatility = sigma_prime

        return final_score, final_deviation, final_volatility

    # step1
    # get data of all the player that will be evaluated on this period
    # Step2 convert the value for glicko usage
    # return a list of players with their games, and glicko data
    def get_data(self, games, season):
        data = []
        for ru in Rating_user.objects.all():
            pr = self.create_pr_if_needed(ru, season)

            player_data = {}
            player_data['username'] = ru.user.username
            player_data['score'] = self.step2_rating(pr.decimal1)
            player_data['deviation'] = self.step2_deviation(pr.decimal2)
            player_data['volatility'] = pr.decimal3

            player_games = []
            for g in games:
                game_data = {}

                participated_in_game = False
                for p in Participant.objects.filter(game = g):
                    if p.user == ru:
                        participated_in_game = True
                        game_data['is_winner'] = 1 if p.team == g.win_team else 0

                if participated_in_game:
                    for p in Participant.objects.filter(game = g):
                        if not p.user == ru:
                            pr = self.create_pr_if_needed(p.user, season)
                            game_data['competitor'] = {}
                            game_data['competitor']['score'] = self.step2_rating(pr.decimal1)
                            game_data['competitor']['deviation'] = self.step2_deviation(pr.decimal2)
                            game_data['competitor']['volatility'] = pr.decimal3
                        
                    
                    player_games.append(game_data)
            if player_games:
                player_data['games'] = player_games
                data.append(player_data)
            else:
                print ("todo: handle standard deviation change for not participating users. User is: ", ru.user.username)
        return data


    def step2_rating(self, r):
        mu = (Decimal(r) - Decimal(1500))/Decimal(173.7178)
        return mu

    def step2_deviation(self, RD):
        phi = Decimal(RD)/Decimal(173.7178)
        return phi

    def step3_E(self, mu, muj, phij):
        power = -self.step3_g(phij)*(mu - muj)
        exponential = Decimal(math.exp(power))
        E = Decimal(1)/(Decimal(1) + exponential)
        return E

    def step3_g(self, phi):
        nominator = Decimal(3 * phi**2)
        denominator = Decimal(math.pi**2)
        g = 1 / (1 + nominator/denominator)**Decimal(0.5)
        return g

    def step3_nu(self, games, mu):
        total_sum = 0
        for game in games:
            E = self.step3_E(mu, game['competitor']['score'], game['competitor']['deviation'])
            g = self.step3_g(game['competitor']['deviation'])
            total_sum += g**Decimal(2)*E*(Decimal(1)-E)
        nu = total_sum**Decimal(-1)
        return nu

    def step4_Delta(self, games, mu, nu):
        total_sum = 0
        for game in games:
            E = self.step3_E(mu, game['competitor']['score'], game['competitor']['deviation'])
            g = self.step3_g(game['competitor']['deviation'])
            total_sum += g*(game['is_winner'] - E)
        Delta = nu*total_sum
        return Delta

    def step5_function_f(self, x, Delta, phi, nu, sigma):
        numerator1 = Delta**Decimal(2) - phi**Decimal(2) - nu- Decimal(math.exp(x))
        numerator1 *= Decimal(math.exp(x))
        denominator1 = phi**Decimal(2) + nu+ Decimal(math.exp(x))
        denominator1 = denominator1 ** Decimal(2)
        denominator1 *= Decimal(2)

        a = Decimal(2)*Decimal(math.log(sigma))
        numerator2 = Decimal(x) - Decimal(a)
        denominator2 = Decimal(self.tau)**Decimal(2)

        result = numerator1 / denominator1
        result -= numerator2 / denominator2
        return result

    def step5_sigma(self, Delta, phi, nu, sigma):
        epsilon = self.epsilon
        a = Decimal(2)*Decimal(math.log(sigma))
        A = Decimal(a)

        if Delta**Decimal(2) > phi**Decimal(2) + nu:
            B = Decimal(math.log(Delta**Decimal(2) - phi**Decimal(2) - nu))
        else:
            k = Decimal(1)
            iteration_num = 0
            while self.step5_function_f(a - Decimal(k)*Decimal(self.tau), Delta, phi, nu, sigma) and iteration_num < self.iteration_limit:
                k += Decimal(1)
                iteration_num += 1
            B = Decimal(a - k*Decimal(self.tau))

        f_A = self.step5_function_f(A, Delta, phi, nu, sigma)
        f_B = self.step5_function_f(B, Delta, phi, nu, sigma)

        iteration_num = 0
        while Decimal(abs(B-A)) > Decimal(epsilon) and iteration_num < self.iteration_limit:
            proportion = f_A / (f_B - f_A)  
            C = A + (A - B) * proportion
            f_C = self.step5_function_f(C, Delta, phi, nu, sigma)

            if f_C*f_B < Decimal(0):
                A = B
                f_A = f_B
            else:
                f_A /= Decimal(2)

            B = C
            f_B = f_C
            iteration_num += 1
        

        sigma_prim = math.exp(A / Decimal(2))
        return sigma_prim

    def step6_phi_star(self, phi, sigma_prime):
        phi_star = (phi**Decimal(2) + Decimal(sigma_prime)**Decimal(2))**Decimal(0.5)
        return phi_star

    def step7_phi_prime(self, phi_star,nu):
        phi_prime = Decimal(1)/((Decimal(1)/phi_star**2)+ (Decimal(1)/nu))**Decimal(0.5)
        return phi_prime

    def step7_mu_prime(self, games, mu, phi_prime):
        total_sum = 0
        for game in games:
            E = self.step3_E(mu, game['competitor']['score'], game['competitor']['deviation'])
            total_sum += self.step3_g(game['competitor']['deviation']) * (game['is_winner'] - E)
        mu_prime = mu + phi_prime**2 * total_sum
        return mu_prime

    def step8_rating(self, mu):
        r = Decimal(173.7178) * mu + Decimal(1500)
        return r
    
    def step8_deviation(self, phi):
        RD = Decimal(173.7178) * phi
        return RD

    def create_pr_if_needed (self, user_obj, season):
        try:
            pr = Player_Rating.objects.get(user=user_obj, rating_type= 3)
        except Player_Rating.DoesNotExist:
            pr = Player_Rating.objects.create(
                user=user_obj, 
                rating_type= 3,
                decimal1 = self.starting_score,
                decimal2 = self.standard_deviation,
                decimal3 = self.volatility,
                season = season,
            )
            pr.save()
        return pr