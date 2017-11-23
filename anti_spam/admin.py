from anti_spam.models import FoundSpam
from django.contrib import admin

class FoundSpamAdmin(admin.ModelsAdmin):
    pass

admin.site.register(FoundSpam, FoundSpamAdmin)