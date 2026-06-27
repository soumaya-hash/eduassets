from django.db import models
from django.conf import settings
from factures.models import Etablissement

class Vehicule(models.Model):
    matricule = models.CharField(max_length=20, unique=True)
    marque = models.CharField(max_length=100)
    modele = models.CharField(max_length=100)
    annee = models.IntegerField()
    kilometrage = models.IntegerField(default=0)
    affectation = models.ForeignKey(Etablissement, on_delete=models.SET_NULL, null=True)
    cree_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.marque} {self.modele} ({self.matricule})"

class ConsommationCarburant(models.Model):
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE)
    date = models.DateField()
    quantite_litres = models.DecimalField(max_digits=6, decimal_places=2)
    cout = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.vehicule} - {self.date}"