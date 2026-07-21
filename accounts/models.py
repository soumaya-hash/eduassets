from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class User(AbstractUser):
    ROLE_CHOICES = [
        ('ADMIN', 'Administrateur Général'),
        ('RESP_FIN', 'Responsable Financier'),
        ('RESP_INFO', 'Responsable Parc Informatique'),
        ('RESP_AUTO', 'Responsable Parc Automobile'),
        ('DP_RESP_FIN', 'Responsable Financier DP'),
        ('DP_RESP_INFO', 'Responsable Parc Informatique DP'),
        ('DP_RESP_AUTO', 'Responsable Parc Automobile DP'),
        ('ETAB_RESP_CONSO', 'Responsable Consommation Etablissement'),
    ]
    ACCESS_LEVEL_CHOICES = [
        ('ACADEMIE', 'Academie'),
        ('DP', 'Direction Provinciale'),
        ('ETABLISSEMENT', 'Etablissement'),
    ]

    cin = models.CharField(max_length=20, unique=True, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='RESP_FIN')
    niveau_acces = models.CharField(max_length=20, choices=ACCESS_LEVEL_CHOICES, default='ACADEMIE')
    academie = models.ForeignKey('factures.Academie', on_delete=models.SET_NULL, null=True, blank=True, related_name='utilisateurs')
    direction_provinciale = models.ForeignKey('factures.DirectionProvinciale', on_delete=models.SET_NULL, null=True, blank=True, related_name='utilisateurs')
    etablissement = models.ForeignKey('factures.Etablissement', on_delete=models.SET_NULL, null=True, blank=True, related_name='utilisateurs')

    ACADEMIE_ROLE_CODES = ('ADMIN', 'RESP_FIN', 'RESP_INFO', 'RESP_AUTO')
    DP_ROLE_CODES = ('DP_RESP_FIN', 'DP_RESP_INFO', 'DP_RESP_AUTO')
    ETABLISSEMENT_ROLE_CODES = ('ETAB_RESP_CONSO',)

    @staticmethod
    def normalize_cin(value):
        if not value:
            return ''
        return ''.join(str(value).upper().split())

    @classmethod
    def build_username_from_cin(cls, cin):
        normalized_cin = cls.normalize_cin(cin)
        if not normalized_cin:
            return ''
        return f'cin_{normalized_cin.lower()}'

    def apply_raf_identity(self, payload):
        self.cin = self.normalize_cin(payload.get('cin', self.cin))
        self.first_name = payload.get('first_name', self.first_name)
        self.last_name = payload.get('last_name', self.last_name)
        self.email = payload.get('email', self.email)
        if not self.username and self.cin:
            self.username = self.build_username_from_cin(self.cin)

    def get_allowed_role_choices(self):
        if self.niveau_acces == 'DP':
            allowed_codes = self.DP_ROLE_CODES
        elif self.niveau_acces == 'ETABLISSEMENT':
            allowed_codes = self.ETABLISSEMENT_ROLE_CODES
        else:
            allowed_codes = self.ACADEMIE_ROLE_CODES
        return [choice for choice in self.ROLE_CHOICES if choice[0] in allowed_codes]

    def get_allowed_role_codes(self):
        return [value for value, _ in self.get_allowed_role_choices()]

    def get_expected_access_level_for_role(self):
        if self.role in self.ACADEMIE_ROLE_CODES:
            return 'ACADEMIE'
        if self.role in self.DP_ROLE_CODES:
            return 'DP'
        if self.role in self.ETABLISSEMENT_ROLE_CODES:
            return 'ETABLISSEMENT'
        return None

    def clean(self):
        super().clean()
        errors = {}

        self.cin = self.normalize_cin(self.cin)

        if self.cin and not self.username:
            self.username = self.build_username_from_cin(self.cin)

        # Allow initial platform administrators to be created before
        # academies / DPs / etablissements are loaded into the system.
        if self.is_superuser and not any([
            self.academie_id,
            self.direction_provinciale_id,
            self.etablissement_id,
        ]):
            return

        expected_level = self.get_expected_access_level_for_role()
        if expected_level and self.niveau_acces != expected_level:
            errors['niveau_acces'] = 'Le niveau d\'acces ne correspond pas au role selectionne.'

        if self.niveau_acces == 'ACADEMIE':
            if not self.academie:
                errors['academie'] = 'Une academie est requise pour ce niveau d\'acces.'
            if self.direction_provinciale:
                errors['direction_provinciale'] = 'Le niveau Academie ne doit pas reference de direction provinciale.'
            if self.etablissement:
                errors['etablissement'] = 'Le niveau Academie ne doit pas reference d\'etablissement.'
        elif self.niveau_acces == 'DP':
            if not self.direction_provinciale:
                errors['direction_provinciale'] = 'Une direction provinciale est requise pour ce niveau d\'acces.'
            if self.etablissement:
                errors['etablissement'] = 'Le niveau DP ne doit pas reference d\'etablissement.'
            if self.direction_provinciale and self.academie and self.academie_id != self.direction_provinciale.academie_id:
                errors['academie'] = 'L\'academie doit correspondre a celle de la direction provinciale.'
            elif self.direction_provinciale and not self.academie:
                self.academie = self.direction_provinciale.academie
        elif self.niveau_acces == 'ETABLISSEMENT':
            if not self.etablissement:
                errors['etablissement'] = 'Un etablissement est requis pour ce niveau d\'acces.'
            if self.etablissement:
                if self.direction_provinciale and self.direction_provinciale_id != self.etablissement.direction_provinciale_id:
                    errors['direction_provinciale'] = 'La direction provinciale doit correspondre a celle de l\'etablissement.'
                elif not self.direction_provinciale:
                    self.direction_provinciale = self.etablissement.direction_provinciale

                expected_academie = None
                if self.etablissement.direction_provinciale:
                    expected_academie = self.etablissement.direction_provinciale.academie

                if self.academie and expected_academie and self.academie_id != expected_academie.id:
                    errors['academie'] = 'L\'academie doit correspondre a celle de l\'etablissement.'
                elif not self.academie:
                    self.academie = expected_academie

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cin or self.username} ({self.get_role_display()})"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['etablissement'],
                condition=Q(role='ETAB_RESP_CONSO', is_active=True, etablissement__isnull=False),
                name='unique_responsable_conso_actif_par_etablissement',
            ),
        ]

class LogActivite(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)
    modele_modifie = models.CharField(max_length=100)
    id_objet = models.IntegerField(null=True, blank=True)
    date_heure = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.utilisateur} - {self.action} - {self.date_heure}"
