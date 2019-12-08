from django.contrib import admin
from .models import Game, Participant, Player_Rating, Rating_user, Season, Tribe, Map, GameType


admin.site.register(Season)
admin.site.register(Tribe)
admin.site.register(Map)
admin.site.register(GameType)


class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'get_user_id', 'game', 'team', 'tribe')

    def get_username(self, obj):
        return obj.user.user.username
    get_username.short_description = 'username'

    def get_user_id(self, obj):
        return obj.user.id
    get_user_id.short_description = 'user id'


admin.site.register(Participant, ParticipantAdmin)


class PlayerRatingAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'rating_type', 'decimal1',
                    'decimal2', 'decimal3', 'season')

    def get_username(self, obj):
        return obj.user.user.username
    get_username.short_description = 'User'


admin.site.register(Player_Rating, PlayerRatingAdmin)


class GameAdmin(admin.ModelAdmin):
    list_display = ('start_date', 'game_type', 'game_map', 'win_team', 'game_status',
                    'game_breaks', 'counted_in_score', 'get_participants', 'get_submitter')

    def get_participants(self, obj):
        for p in Participant.objects.filter(game=obj):
            return p.user.user.username
    get_participants.short_description = 'Participant'

    def get_submitter(self, obj):
        return obj.submitter
    get_submitter.short_description = 'submitter'


admin.site.register(Game, GameAdmin)


class RatingUserAdmin(admin.ModelAdmin):
    list_display = ('get_user', 'id')

    def get_user(self, obj):
        return obj.user.username
    get_user.short_description = 'User'


admin.site.register(Rating_user, RatingUserAdmin)
