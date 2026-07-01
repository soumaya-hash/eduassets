from django.contrib import admin
from .models import Facture, Etablissement


@admin.register(Etablissement)
class EtablissementAdmin(admin.ModelAdmin):
    """Admin interface for institution management"""
    list_display = ['nom', 'adresse', 'ville']
    search_fields = ['nom', 'adresse']
    fieldsets = (
        ('Informations', {
            'fields': ['nom', 'adresse', 'ville']
        }),
    )


@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    """Admin interface for invoice management"""
    list_display = ['reference', 'etablissement', 'type_facture', 'montant', 'statut', 'date_emission', 'cree_par']
    list_filter = ['statut', 'type_facture', 'date_emission', 'etablissement']
    search_fields = ['reference', 'etablissement__nom']
    readonly_fields = ['cree_par', 'date_creation']
    date_hierarchy = 'date_emission'

    fieldsets = (
        ('Facture', {
            'fields': ['reference', 'type_facture', 'etablissement', 'montant']
        }),
        ('Dates', {
            'fields': ['date_emission', 'date_echeance']
        }),
        ('Paiement', {
            'fields': ['statut']
        }),
        ('Suivi', {
            'fields': ['cree_par', 'date_creation'],
            'classes': ['collapse']
        }),
    )

    def save_model(self, request, obj, form, change):
        """Automatically set cree_par to current user"""
        if not change:
            obj.cree_par = request.user
        super().save_model(request, obj, form, change)

