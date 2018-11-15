from django.contrib import admin
from .models import Participant, Schedule

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    pass

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    pass
