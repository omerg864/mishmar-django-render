from django.contrib import admin
from .models import UserSettings
from django.contrib.auth.models import User

# Register your models here.


class ProfileAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('user', "name", 'nickname', 'sat',
                    'night', 'sat_night', 'sat_morning', 'sat_noon', 'language')
    list_editable = ('nickname', 'sat', 'night', 'sat_night', 'sat_morning', 'sat_noon', 'language')
    search_fields = ['=user__username', ]

    def name(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'


admin.site.register(UserSettings, ProfileAdmin)
