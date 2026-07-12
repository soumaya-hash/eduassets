from django.db import models
from django.conf import settings
from factures.models import Etablissement

class EquipementInformatique(models.Model):
    # --- Liste des désignations possibles ---
    DESIGNATION_CHOICES = [
        ('ECRAN', 'Écran'),
        ('UNITE_CENTRALE', 'Unité centrale'),
        ('CLAVIER', 'Clavier'),
        ('SOURIS', 'Souris'),
        ('IMPRIMANTE', 'Imprimante'),
        ('SCANNER', 'Scanner'),
        ('ONDULEUR', 'Onduleur'),
        ('DISQUE_DUR', 'Disque dur externe'),
        ('AUTRE', 'Autre'),
    ]

    ETAT_CHOICES = [
        ('FONCTIONNEL', 'Fonctionnel'),
        ('EN_MAINTENANCE', 'En maintenance'),
        ('HORS_SERVICE', 'Hors service'),
    ]

    numero_inventaire = models.CharField(max_length=50, unique=True)
    # --- Modification du champ designation avec choix ---
    designation = models.CharField(
        max_length=50,  # on réduit car les choix font ~20 caractères max
        choices=DESIGNATION_CHOICES,
        default='AUTRE',
        verbose_name="Désignation"
    )
    marque = models.CharField(max_length=100)
    modele = models.CharField(max_length=100)
    date_acquisition = models.DateField()
    etablissement = models.ForeignKey(Etablissement, on_delete=models.CASCADE)
    etat = models.CharField(max_length=20, choices=ETAT_CHOICES, default='FONCTIONNEL')
    cree_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.get_designation_display()} ({self.numero_inventaire})"