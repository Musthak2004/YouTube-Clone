from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    list_display = ('username', 'email', 'is_staff', 'is_superuser')

    fieldsets = UserAdmin.fieldsets + (
        ("Profile", {'fields': ('profile_picture', 'bio')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)