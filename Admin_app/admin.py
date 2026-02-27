from django.contrib import admin
from Core_app.models import User   
from django.contrib.auth.admin import UserAdmin

admin.site.register(User,UserAdmin)

