from django.contrib import admin
from .models import (
    Facture,
    Etablissement,
    Academie,
    DirectionProvinciale,
    Commune,
    Compteur,
    SaisieConsommationMensuelle,
    AlerteConsommation,
)


@admin.register(Academie)
class AcademieAdmin(admin.ModelAdmin):
    list_display = ['code', 'nom']
    search_fields = ['code', 'nom']


@admin.register(DirectionProvinciale)
class DirectionProvincialeAdmin(admin.ModelAdmin):
    list_display = ['code', 'nom', 'academie']
    list_filter = ['academie']
    search_fields = ['code', 'nom', 'academie__nom']


@admin.register(Commune)
class CommuneAdmin(admin.ModelAdmin):
    list_display = ['code', 'nom', 'direction_provinciale']
    list_filter = ['direction_provinciale__academie', 'direction_provinciale']
    search_fields = ['nom', 'direction_provinciale__nom']


@admin.register(Etablissement)
class EtablissementAdmin(admin.ModelAdmin):
    """Admin interface for institution management"""
    list_display = ['nom', 'identifiant_unique', 'type_etablissement', 'academie', 'direction_provinciale', 'commune', 'cycle', 'actif']
    list_filter = ['actif', 'type_etablissement', 'cycle', 'academie', 'direction_provinciale']
    search_fields = ['nom', 'nom_arabe', 'identifiant_unique', 'adresse', 'ville']
    fieldsets = (
        ('Informations', {
            'fields': [
                'identifiant_unique', 'nom', 'nom_arabe', 'type_etablissement', 'code_milieu',
                'academie', 'direction_provinciale', 'commune', 'etablissement_rattachement', 'cycle', 'actif',
            ]
        }),
        ('Adresse', {
            'fields': ['adresse', 'ville']
        }),
    )


@admin.register(Compteur)
class CompteurAdmin(admin.ModelAdmin):
    list_display = ['libelle', 'fournisseur', 'etablissement', 'type_compteur', 'numero_contrat', 'code_compteur', 'actif']
    list_filter = ['actif', 'fournisseur', 'type_compteur', 'etablissement__direction_provinciale']
    search_fields = ['libelle', 'numero_contrat', 'code_compteur', 'etablissement__nom']


@admin.register(SaisieConsommationMensuelle)
class SaisieConsommationMensuelleAdmin(admin.ModelAdmin):
    list_display = ['etablissement', 'compteur', 'annee', 'mois', 'quantite_consommee', 'montant_theorique', 'montant_fournisseur', 'statut_saisie']
    list_filter = ['annee', 'mois', 'statut_saisie', 'compteur__type_compteur']
    search_fields = ['etablissement__nom', 'compteur__libelle', 'compteur__numero_contrat']
    readonly_fields = ['quantite_consommee', 'montant_theorique', 'ecart_montant', 'taux_ecart', 'date_saisie']


@admin.register(AlerteConsommation)
class AlerteConsommationAdmin(admin.ModelAdmin):
    list_display = ['etablissement', 'niveau_alerte', 'type_alerte', 'traitee', 'date_creation']
    list_filter = ['niveau_alerte', 'type_alerte', 'traitee', 'direction_provinciale', 'academie']
    search_fields = ['message', 'etablissement__nom', 'compteur__libelle']
    readonly_fields = ['date_creation']


@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    """Admin interface for invoice management"""
    list_display = ['reference', 'etablissement', 'fournisseur', 'compteur', 'type_facture', 'montant', 'statut', 'date_emission', 'cree_par']
    list_filter = ['statut', 'fournisseur', 'type_facture', 'date_emission', 'etablissement', 'compteur']
    search_fields = ['reference', 'numero_contrat', 'etablissement__nom', 'compteur__libelle']
    readonly_fields = ['cree_par', 'date_creation']
    date_hierarchy = 'date_emission'

    fieldsets = (
        ('Facture', {
            'fields': ['reference', 'type_facture', 'etablissement', 'fournisseur', 'compteur', 'numero_contrat', 'montant']
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

