from django.contrib import admin
from .models import EquipementInformatique


@admin.register(EquipementInformatique)
class EquipementInformatiqueAdmin(admin.ModelAdmin):
    """Admin interface for IT equipment management"""
    list_display = ['numero_inventaire', 'designation', 'marque', 'etat', 'etablissement', 'date_acquisition', 'cree_par']
    list_filter = ['etat', 'date_acquisition', 'etablissement']
    search_fields = ['numero_inventaire', 'designation', 'marque']
    readonly_fields = ['cree_par']
    date_hierarchy = 'date_acquisition'

    fieldsets = (
        ('Équipement', {
            'fields': ['numero_inventaire', 'designation', 'marque', 'modele']
        }),
        ('Détails', {
            'fields': ['etablissement', 'date_acquisition']
        }),
        ('État', {
            'fields': ['etat']
        }),
        ('Suivi', {
            'fields': ['cree_par'],
            'classes': ['collapse']
        }),
    )

    def save_model(self, request, obj, form, change):
        """Automatically set cree_par to current user"""
        if not change:
            obj.cree_par = request.user
        super().save_model(request, obj, form, change)

