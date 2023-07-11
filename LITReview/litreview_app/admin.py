from django.contrib import admin
from .models import Ticket, Review, UserFollows
# Register your models here.
class TicketModelAdmin(admin.ModelAdmin):
    list_display = ('title', 'time_created')
    list_filter = ('title', 'time_created')
    search_fields = ('title',)

# ∫admin.site.register(TicketModelAdmin)
admin.site.register(Ticket, TicketModelAdmin)
admin.site.register(UserFollows)
admin.site.register(Review)
