from django.contrib import admin
from .models import Game, Participant, Player_Rating, Temporary_user, Season


admin.site.register(Participant)
admin.site.register(Player_Rating)
admin.site.register(Temporary_user)
admin.site.register(Season)


class GameAdmin(admin.ModelAdmin):
    list_display = ('start_date', 'game_type', 'game_map', 'win_team', 'game_status', 'game_breaks', 'counted_in_score', 'get_participants')

    def get_participants(self, obj):
        for p in Participant.objects.filter(game = obj):    
            return p
    get_participants.short_description = 'Participant'

admin.site.register(Game, GameAdmin)

