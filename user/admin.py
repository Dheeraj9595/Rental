from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(User)
admin.site.register(House)
admin.site.register(Cloth)
admin.site.register(Room)
admin.site.register(Contact)
