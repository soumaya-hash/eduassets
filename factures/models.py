from django.db import models
from django.conf import settings

class Etablissement(models.Model):
    nom = models.CharField(max_length=200)
    adresse = models.TextField(blank=True, null=True)
    ville = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.nom

class Facture(models.Model):
    TYPE_CHOICES = [('EAU', 'Eau'), ('ELECTRICITE', 'Électricité')]
    STATUT_CHOICES = [
        ('PAYEE', 'Payée'),
        ('EN_ATTENTE', 'En attente'),
        ('EN_RETARD', 'En retard'),
    ]
    etablissement = models.ForeignKey(Etablissement, on_delete=models.CASCADE)
    type_facture = models.CharField(max_length=15, choices=TYPE_CHOICES)
    reference = models.CharField(max_length=100, unique=True)
    date_emission = models.DateField()
    date_echeance = models.DateField()
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    statut = models.CharField(max_length=15, choices=STATUT_CHOICES, default='EN_ATTENTE')
    cree_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type_facture} - {self.reference}"