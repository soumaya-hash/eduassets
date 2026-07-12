from django.urls import path
from . import views

urlpatterns = [
    path('', views.liste_factures, name='liste_factures'),
    path('ajouter/', views.ajouter_facture, name='ajouter_facture'),
    path('modifier/<int:pk>/', views.modifier_facture, name='modifier_facture'),
    path('supprimer/<int:pk>/', views.supprimer_facture, name='supprimer_facture'),
    path('etablissement/', views.tableau_consumption_etablissement, name='tableau_consumption_etablissement'),
    path('etablissement/saisies/', views.saisie_consommation_liste, name='saisie_consommation_liste'),
    path('etablissement/saisies/ajouter/', views.saisie_consommation_creer, name='saisie_consommation_creer'),
    path('etablissement/saisies/<int:pk>/modifier/', views.saisie_consommation_modifier, name='saisie_consommation_modifier'),
    path('etablissement/saisies/<int:pk>/supprimer/', views.saisie_consommation_supprimer, name='saisie_consommation_supprimer'),
    path('etablissement/factures/', views.factures_etablissement, name='factures_etablissement'),
    path('etablissement/alertes/', views.alertes_etablissement, name='alertes_etablissement'),
    path('dp/saisies-a-controler/', views.saisies_a_controler_dp, name='saisies_a_controler_dp'),
    path('dp/saisies/<int:pk>/controler/', views.controler_saisie_dp, name='controler_saisie_dp'),
    path('dp/alertes/', views.alertes_dp, name='alertes_dp'),
    path('dp/alertes/<int:pk>/traiter/', views.traiter_alerte_dp, name='traiter_alerte_dp'),
]
