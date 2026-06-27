from django.db import models
from django.conf import settings
from factures.models import Etablissement

class EquipementInformatique(models.Model):
    ETAT_CHOICES = [
        ('FONCTIONNEL', 'Fonctionnel'),
        ('EN_MAINTENANCE', 'En maintenance'),
        ('HORS_SERVICE', 'Hors service'),
    ]
    numero_inventaire = models.CharField(max_length=50, unique=True)
    designation = models.CharField(max_length=200)
    marque = models.CharField(max_length=100)
    modele = models.CharField(max_length=100)
    date_acquisition = models.DateField()
    etablissement = models.ForeignKey(Etablissement, on_delete=models.CASCADE)
    etat = models.CharField(max_length=20, choices=ETAT_CHOICES, default='FONCTIONNEL')
    cree_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.designation} ({self.numero_inventaire})"