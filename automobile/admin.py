from django.contrib import admin
from .models import Vehicule, ConsommationCarburant, Mission


@admin.register(Vehicule)
class VehiculeAdmin(admin.ModelAdmin):
    """Admin interface for vehicle management"""
    list_display = ['matricule', 'marque', 'modele', 'annee', 'kilometrage', 'affectation', 'cree_par']
    list_filter = ['affectation']
    search_fields = ['matricule', 'marque', 'modele']
    readonly_fields = ['cree_par']
    fieldsets = (
        ('Informations Véhicule', {
            'fields': ['matricule', 'marque', 'modele', 'annee', 'kilometrage']
        }),
        ('Affectation', {
            'fields': ['affectation']
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


@admin.register(ConsommationCarburant)
class ConsommationCarburantAdmin(admin.ModelAdmin):
    """Admin interface for fuel consumption tracking"""
    list_display = ['vehicule', 'date', 'quantite_litres', 'cout']
    list_filter = ['vehicule', 'date']
    search_fields = ['vehicule__matricule', 'vehicule__marque']
    fieldsets = (
        ('Véhicule', {
            'fields': ['vehicule']
        }),
        ('Consommation', {
            'fields': ['date', 'quantite_litres', 'cout']
        }),
    )


@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ['reference_om', 'date_mission', 'vehicule', 'destination', 'conducteur', 'distance_parcourue', 'montant_carburant']
    list_filter = ['date_mission', 'vehicule']
    search_fields = ['reference_om', 'destination', 'conducteur', 'vehicule__matricule']
    readonly_fields = ['distance_parcourue', 'cree_par', 'date_creation']

    def save_model(self, request, obj, form, change):
        if not change:
            obj.cree_par = request.user
        super().save_model(request, obj, form, change)

