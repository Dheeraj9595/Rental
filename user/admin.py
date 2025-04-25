from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(User)
admin.site.register(House)
# admin.site.register(Cloth)
admin.site.register(Room)
admin.site.register(Contact)

from django.contrib import admin
from user.models import Cloth

@admin.register(Cloth)
class ClothAdmin(admin.ModelAdmin):
    list_display = ('type', 'user_email', 'is_approved', 'availability', 'date_added')
    list_filter = ('is_approved', 'availability', 'type')
    actions = ['approve_cloths', 'reject_cloths']
    search_fields = ('type', 'user_email__email')

    def approve_cloths(self, request, queryset):
        queryset.update(is_approved=True)
    approve_cloths.short_description = "Mark selected cloths as approved"

    def reject_cloths(self, request, queryset):
        queryset.update(is_approved=False)
    reject_cloths.short_description = "Mark selected cloths as rejected"

