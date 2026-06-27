from django.db import models
from django.conf import settings
from informatique.models import EquipementInformatique
from automobile.models import Vehicule

class Maintenance(models.Model):
    CIBLE_CHOICES = [
        ('INFORMATIQUE', 'Informatique'),
        ('AUTOMOBILE', 'Automobile'),
    ]
    STATUT_CHOICES = [
        ('PLANIFIEE', 'Planifiée'),
        ('EN_COURS', 'En cours'),
        ('TERMINEE', 'Terminée'),
    ]
    type_cible = models.CharField(max_length=15, choices=CIBLE_CHOICES)
    equipement = models.ForeignKey(EquipementInformatique, on_delete=models.CASCADE, null=True, blank=True)
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField()
    date_intervention = models.DateField()
    cout = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    statut = models.CharField(max_length=15, choices=STATUT_CHOICES, default='PLANIFIEE')
    cree_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Maintenance {self.get_type_cible_display()} - {self.date_intervention}"