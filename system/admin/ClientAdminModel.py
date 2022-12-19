from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from system.models.ClientModel import Client
from django.utils.translation import gettext_lazy as _

# The custom admin change form.
class ClientChangeForm(UserChangeForm):
    # The Meta information.
    class Meta(UserChangeForm.Meta):
        # The model used for the form.
        model = Client


# The custom admin.
@admin.register(Client)
class ClientAdmin(UserAdmin):
    # The form for this admin.
    form = ClientChangeForm

    # The custom fieldsets.
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('full_name',)}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
