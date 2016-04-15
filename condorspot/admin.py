from django.contrib import admin
from condor.condorspot.models import Task, Competition, SprintResult, Turnpoint, Event

class SprintResultAdmin(admin.ModelAdmin):
    list_filter = ['callsign', 'firstname', 'lastname']
    search_fields = ['callsign', 'firstname', 'lastname', 'registration_number']
    date_hierarchy = 'date'
    list_display = ('taskname', 'firstname', 'lastname', 'callsign', 'registration_number', 'speed', 'date')


admin.site.register(Competition)
admin.site.register(Event)
admin.site.register(Task)
admin.site.register(Turnpoint)
admin.site.register(SprintResult, SprintResultAdmin)