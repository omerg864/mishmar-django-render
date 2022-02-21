from django.contrib import admin
from .models import Post
from .models import Event
from .models import IpBan
from .models import Week
from .models import ShiftWeek
from .models import Gun
from .models import Arming_Log
from .models import ValidationLog
from .models import ArmingRequest
from .models import OrganizationShift
from .models import Shift as Shift
from .models import Organization1 as Organization

admin.site.register(Shift)
admin.site.register(ShiftWeek)


class EventAdmin(admin.ModelAdmin):
    list_display = ("date2", "nickname", "description")


admin.site.register(Organization)
admin.site.register(OrganizationShift)
admin.site.register(Post)
admin.site.register(Week)
admin.site.register(Event, EventAdmin)
admin.site.register(IpBan)
admin.site.register(Gun)
admin.site.register(Arming_Log)
admin.site.register(ValidationLog)
admin.site.register(ArmingRequest)
# Register your models here.
