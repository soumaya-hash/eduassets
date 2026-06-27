from django.urls import path
from . import views

urlpatterns = [
    path('', views.liste_factures, name='liste_factures'),
    path('ajouter/', views.ajouter_facture, name='ajouter_facture'),
    path('modifier/<int:pk>/', views.modifier_facture, name='modifier_facture'),
    path('supprimer/<int:pk>/', views.supprimer_facture, name='supprimer_facture'),
]