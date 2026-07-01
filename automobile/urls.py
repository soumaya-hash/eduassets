from django.urls import path
from . import views

urlpatterns = [
    path('', views.liste_vehicules, name='liste_vehicules'),
    path('ajouter/', views.ajouter_vehicule, name='ajouter_vehicule'),
    path('modifier/<int:pk>/', views.modifier_vehicule, name='modifier_vehicule'),
    path('supprimer/<int:pk>/', views.supprimer_vehicule, name='supprimer_vehicule'),
    path('consommations/', views.liste_consommations, name='liste_consommations'),
    path('consommations/ajouter/', views.ajouter_consommation, name='ajouter_consommation'),
]
