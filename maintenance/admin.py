from django.contrib import admin
from .models import Maintenance


@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    """Admin interface for maintenance tracking"""
    list_display = ['get_asset_name', 'type_cible', 'type_intervention', 'date_intervention', 'cout', 'statut', 'cree_par']
    list_filter = ['type_cible', 'type_intervention', 'statut', 'date_intervention']
    search_fields = ['description', 'lieu', 'reference_facture', 'equipement__designation', 'vehicule__matricule']
    readonly_fields = ['cree_par']
    date_hierarchy = 'date_intervention'
    
    fieldsets = (
        ('Maintenance', {
            'fields': ['type_cible', 'type_intervention', 'description', 'equipement', 'vehicule']
        }),
        ('Détails', {
            'fields': [
                'date_intervention', 'lieu', 'kilometrage_intervention', 'cout', 'reference_facture',
                'pieces_remplacees', 'prochaine_echeance', 'prochain_kilometrage', 'statut'
            ]
        }),
        ('Suivi', {
            'fields': ['cree_par'],
            'classes': ['collapse']
        }),
    )

    def get_asset_name(self, obj):
        """Display the equipment or vehicle name"""
        if obj.equipement:
            return f"IT: {obj.equipement.designation}"
        elif obj.vehicule:
            return f"Auto: {obj.vehicule.matricule}"
        return "N/A"
    get_asset_name.short_description = "Ressource"

    def save_model(self, request, obj, form, change):
        """Automatically set cree_par to current user"""
        if not change:
            obj.cree_par = request.user
        super().save_model(request, obj, form, change)

