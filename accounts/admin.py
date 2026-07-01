from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, LogActivite


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Admin interface for custom user management"""
    list_display = ['username', 'get_full_name', 'role', 'is_staff', 'is_active']
    list_filter = ['role', 'is_staff', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    fieldsets = UserAdmin.fieldsets + (
        ('Rôle', {'fields': ('role',)}),
    )

    def get_full_name(self, obj):
        """Display full name"""
        return obj.get_full_name() or obj.username
    get_full_name.short_description = 'Nom Complet'


@admin.register(LogActivite)
class LogActiviteAdmin(admin.ModelAdmin):
    """Admin interface for activity log viewing"""
    list_display = ['utilisateur', 'action', 'modele_modifie', 'date_heure']
    list_filter = ['modele_modifie', 'date_heure', 'utilisateur']
    search_fields = ['utilisateur__username', 'action', 'modele_modifie']
    readonly_fields = ['utilisateur', 'action', 'modele_modifie', 'id_objet', 'date_heure']
    date_hierarchy = 'date_heure'
    
    def has_add_permission(self, request):
        """Prevent manual creation of log entries"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of log entries"""
        return False

    def has_change_permission(self, request, obj=None):
        """Prevent editing of log entries"""
        return False