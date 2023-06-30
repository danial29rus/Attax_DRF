from django.contrib import admin
from .models import Participant, Match, Like


class ParticipantAdmin(admin.ModelAdmin):
    list_display = ['id']


admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Match)
admin.site.register(Like)
