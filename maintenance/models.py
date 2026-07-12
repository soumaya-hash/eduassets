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
    TYPE_INTERVENTION_CHOICES = [
        ('VISITE_TECHNIQUE', 'Visite technique'),
        ('VIDANGE', 'Vidange'),
        ('REPARATION', 'Réparation'),
        ('PNEUMATIQUES', 'Pneumatiques'),
        ('FREINAGE', 'Freinage'),
        ('CARROSSERIE', 'Carrosserie'),
        ('ASSURANCE', 'Assurance'),
        ('AUTRE', 'Autre'),
    ]
    TYPE_MAINTENANCE_INFO_CHOICES = [
        ('CORRECTIVE', 'Corrective'),
        ('PREVENTIVE', 'Préventive'),
        ('INSTALLATION_CONFIGURATION', 'Installation / configuration'),
        ('REMPLACEMENT', 'Remplacement'),
        ('AUTRE', 'Autre'),
    ]
    type_cible = models.CharField(max_length=15, choices=CIBLE_CHOICES)
    equipement = models.ForeignKey(EquipementInformatique, on_delete=models.CASCADE, null=True, blank=True)
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField()
    type_intervention = models.CharField(
        max_length=30, choices=TYPE_INTERVENTION_CHOICES, null=True, blank=True
    )
    type_maintenance_info = models.CharField(
        max_length=30, choices=TYPE_MAINTENANCE_INFO_CHOICES, null=True, blank=True
    )
    panne_signalee = models.TextField(blank=True)
    diagnostic = models.TextField(blank=True)
    prestataire = models.CharField(max_length=200, blank=True)
    date_intervention = models.DateField()
    lieu = models.CharField(max_length=200, blank=True)
    kilometrage_intervention = models.PositiveIntegerField(null=True, blank=True)
    cout = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    reference_facture = models.CharField(max_length=100, blank=True)
    pieces_remplacees = models.TextField(blank=True)
    prochaine_echeance = models.DateField(null=True, blank=True)
    prochain_kilometrage = models.PositiveIntegerField(null=True, blank=True)
    statut = models.CharField(max_length=15, choices=STATUT_CHOICES, default='PLANIFIEE')
    cree_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Maintenance {self.get_type_cible_display()} - {self.date_intervention}"
