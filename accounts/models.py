from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('ADMIN', 'Administrateur Général'),
        ('RESP_FIN', 'Responsable Financier'),
        ('RESP_INFO', 'Responsable Parc Informatique'),
        ('RESP_AUTO', 'Responsable Parc Automobile'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='RESP_FIN')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class LogActivite(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)
    modele_modifie = models.CharField(max_length=100)
    id_objet = models.IntegerField(null=True, blank=True)
    date_heure = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.utilisateur} - {self.action} - {self.date_heure}"