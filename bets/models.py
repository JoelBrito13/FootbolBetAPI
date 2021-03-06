from django.core.exceptions import ValidationError
import datetime
import requests
import json
from django.db import models
from users.models import Person

URL_UPDATE = "https://apiv2.apifootball.com/" \
                 "?action=get_predictions" \
                 "&APIkey=2460239a218e22dd4c13f692c3caedafd1ef37cfc2fcbe58e645065c1fefd9d3"
class Game(models.Model):
    # Constants in Model class

    match_id = models.IntegerField(primary_key=True)
    country_name = models.CharField(max_length=50)
    league_name = models.CharField(max_length=70)
    match_date = models.DateField()
    match_status = models.CharField(max_length=50, null=True)
    match_time = models.TimeField()
    match_hometeam_name = models.CharField(max_length=70)
    match_hometeam_score = models.IntegerField(null=True)
    match_awayteam_name = models.CharField(max_length=70)
    match_awayteam_score = models.IntegerField(null=True)
    prob_HW = models.FloatField()
    prob_D = models.FloatField()
    prob_AW = models.FloatField()

    def update(self):
        if self.match_finished() and not self.match_status == 'Finished':
            url = "{}&match_id={}".format(URL_UPDATE, self.match_id)
            jsonResponse = self.make_request(url)[0]
            self.match_status = jsonResponse['match_status']
            self.match_hometeam_score = jsonResponse['match_hometeam_score']
            self.match_awayteam_score = jsonResponse['match_awayteam_score']
            self.save()

    def match_finished(self):
        return self.match_date < datetime.date.today()

    def add_game(self, search_id):
        current = Game.objects.filter(match_id=search_id)
        if not current:
            url = "{}&match_id={}".format(URL_UPDATE, search_id)
            json_response = self.make_request(url)[0]

            self.match_id = int(json_response['match_id'])
            self.country_name = json_response['country_name']
            self.league_name = json_response['league_name']
            self.match_date = json_response['match_date']
            self.match_status = json_response['match_status']
            self.match_time = json_response['match_time']
            self.match_hometeam_name = json_response['match_hometeam_name']
            self.match_awayteam_name = json_response['match_awayteam_name']
            self.prob_HW = float(json_response['prob_HW'])
            self.prob_D = float(json_response['prob_D'])
            self.prob_AW = float(json_response['prob_AW'])

            self.save()
            return self

        return current

    def save(self, **kwargs):
        if Game.objects.exists() and not self.pk:
            raise ValidationError('Error Saving Game')
        return super().save(**kwargs)

    @staticmethod
    def make_request(url):
        myResponse = requests.get(url, verify=True)
        if (myResponse.ok):
            return json.loads(myResponse.content)
        return myResponse.raise_for_status()  # Error in request

    def __str__(self):
        return "{} match: {}, {} x {} - {}".format(self.league_name,
                                                   self.match_id,
                                                   self.match_hometeam_name,
                                                   self.match_awayteam_name,
                                                   self.match_date)


class Bet(models.Model):
    # Constants in Model class
    HOME_WIN = 'HW'
    DRAW = 'D'
    AWAY_WIN = 'AW'
    GAME_RESULTS = (
        (HOME_WIN, 'Home Win'),
        (DRAW, 'Draw'),
        (AWAY_WIN, 'Away Win')
    )
    game = models.ForeignKey(Game,
                             on_delete=models.CASCADE)
    user = models.ForeignKey(Person,
                             on_delete=models.CASCADE)
    game_bet = models.CharField(
        max_length=2,
        choices=GAME_RESULTS
    )
    amount = models.FloatField(null=False,
                               default=0)
    game_finished = models.BooleanField(
        default=False
    )
    balance = models.FloatField(
        default=0
    )

    def update_status(self):
        if self.game_finished:
            return
        self.game.update()
        if self.game.match_status == 'Finished':
            self.define_profit()  # self.balance = profit of the game
            self.user.insert_credits(
                self.balance
            )

            self.game_finished = True
            self.save()

    def define_profit(self):
        if self.game_bet == self.define_result():
            self.balance = self.amount * 100 / self.get_prob()
        return self.balance

    def define_result(self):
        home = self.game.match_hometeam_score
        away = self.game.match_awayteam_score
        print(self.__str__())
        if home > away:
            return self.HOME_WIN
        elif home < away:
            return self.AWAY_WIN
        else:
            return self.DRAW

    def get_prob(self):
        if self.game_bet == self.HOME_WIN:
            return self.game.prob_HW
        if self.game_bet == self.AWAY_WIN:
            return self.game.prob_AW
        if self.game_bet == self.DRAW:
            return self.game.prob_D

    def __str__(self):
        return "{} Bet ({} bet: {},{}€ profit:{})".format(self.user, self.game, self.game_bet, self.amount,
                                                          self.balance)
