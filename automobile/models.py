from django.core.exceptions import ValidationError
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


class Mission(models.Model):
    """Ordre de mission effectué avec un véhicule du parc automobile."""

    vehicule = models.ForeignKey(
        Vehicule,
        on_delete=models.PROTECT,
        related_name='missions',
    )
    reference_om = models.CharField("Référence OM", max_length=50, unique=True)
    date_mission = models.DateField("Date de mission")
    lieu_depart = models.CharField("Lieu de départ", max_length=150)
    destination = models.CharField(max_length=150)
    conducteur = models.CharField(max_length=150)
    objet = models.CharField("Objet de la mission", max_length=250, blank=True)
    kilometrage_depart = models.PositiveIntegerField("Kilométrage au départ")
    kilometrage_arrivee = models.PositiveIntegerField("Kilométrage à l'arrivée")
    distance_parcourue = models.PositiveIntegerField(editable=False, default=0)
    montant_carburant = models.DecimalField(
        "Montant du carburant (DH)", max_digits=10, decimal_places=2, null=True, blank=True
    )
    observation = models.TextField(blank=True)
    cree_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_mission', '-id']
        verbose_name = 'mission'
        verbose_name_plural = 'missions'

    def clean(self):
        super().clean()
        if (
            self.kilometrage_depart is not None
            and self.kilometrage_arrivee is not None
            and self.kilometrage_arrivee < self.kilometrage_depart
        ):
            raise ValidationError({
                'kilometrage_arrivee': "Le kilométrage d'arrivée doit être supérieur ou égal au kilométrage de départ."
            })
        if self.kilometrage_depart is not None and self.kilometrage_arrivee is not None:
            self.distance_parcourue = self.kilometrage_arrivee - self.kilometrage_depart

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference_om} - {self.destination}"
