from django.contrib import admin

from .models import Participant, Troop


class ParticipantInline(admin.TabularInline):
    model = Participant


class TroopAdmin(admin.ModelAdmin):
    inlines = [ParticipantInline,]

admin.site.register(Participant)
admin.site.register(Troop, TroopAdmin)

