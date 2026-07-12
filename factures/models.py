from decimal import Decimal

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Academie(models.Model):
    code = models.CharField(max_length=30, unique=True)
    nom = models.CharField(max_length=200)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.nom}"


class DirectionProvinciale(models.Model):
    code = models.CharField(max_length=30, unique=True)
    nom = models.CharField(max_length=200)
    academie = models.ForeignKey(Academie, on_delete=models.CASCADE, related_name='directions_provinciales')

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.nom}"


class Commune(models.Model):
    code = models.CharField(max_length=30, null=True, blank=True)
    nom = models.CharField(max_length=150)
    direction_provinciale = models.ForeignKey(DirectionProvinciale, on_delete=models.CASCADE, related_name='communes')

    class Meta:
        ordering = ['nom']
        constraints = [
            models.UniqueConstraint(
                fields=['nom', 'direction_provinciale'],
                name='unique_commune_nom_par_dp',
            ),
            models.UniqueConstraint(
                fields=['code', 'direction_provinciale'],
                name='unique_commune_code_par_dp',
            ),
        ]

    def __str__(self):
        return self.nom


class Etablissement(models.Model):
    CYCLE_CHOICES = [
        ('PRIMAIRE', 'Primaire'),
        ('COLLEGE', 'College'),
        ('LYCEE', 'Lycee'),
    ]

    identifiant_unique = models.CharField(max_length=50, unique=True, null=True, blank=True)
    nom = models.CharField(max_length=200)
    nom_arabe = models.CharField(max_length=250, blank=True, null=True)
    type_etablissement = models.CharField(max_length=30, blank=True, null=True)
    code_milieu = models.CharField(max_length=30, blank=True, null=True)
    academie = models.ForeignKey(Academie, on_delete=models.SET_NULL, null=True, blank=True, related_name='etablissements')
    direction_provinciale = models.ForeignKey(DirectionProvinciale, on_delete=models.SET_NULL, null=True, blank=True, related_name='etablissements')
    commune = models.ForeignKey(Commune, on_delete=models.SET_NULL, null=True, blank=True, related_name='etablissements')
    etablissement_rattachement = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='etablissements_rattaches',
    )
    cycle = models.CharField(max_length=20, choices=CYCLE_CHOICES, null=True, blank=True)
    adresse = models.TextField(blank=True, null=True)
    ville = models.CharField(max_length=100, blank=True, null=True)
    actif = models.BooleanField(default=True)

    class Meta:
        ordering = ['nom']

    def clean(self):
        super().clean()
        errors = {}

        if self.commune:
            if self.direction_provinciale and self.direction_provinciale_id != self.commune.direction_provinciale_id:
                errors['direction_provinciale'] = 'La direction provinciale doit correspondre a celle de la commune.'
            elif not self.direction_provinciale:
                self.direction_provinciale = self.commune.direction_provinciale

        if self.direction_provinciale:
            if self.academie and self.academie_id != self.direction_provinciale.academie_id:
                errors['academie'] = 'L\'academie doit correspondre a celle de la direction provinciale.'
            elif not self.academie:
                self.academie = self.direction_provinciale.academie

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.nom


class Compteur(models.Model):
    TYPE_CHOICES = [
        ('EAU', 'Eau'),
        ('ELECTRICITE', 'Electricite'),
    ]

    etablissement = models.ForeignKey(Etablissement, on_delete=models.CASCADE, related_name='compteurs')
    type_compteur = models.CharField(max_length=20, choices=TYPE_CHOICES)
    numero_contrat = models.CharField(max_length=100, unique=True)
    code_compteur = models.CharField(max_length=100)
    libelle = models.CharField(max_length=200)
    actif = models.BooleanField(default=True)

    class Meta:
        ordering = ['etablissement__nom', 'type_compteur', 'libelle']
        constraints = [
            models.UniqueConstraint(
                fields=['etablissement', 'type_compteur', 'code_compteur'],
                name='unique_compteur_par_etablissement_type_code',
            ),
        ]

    def __str__(self):
        return f"{self.etablissement} - {self.get_type_compteur_display()} - {self.libelle}"


class SaisieConsommationMensuelle(models.Model):
    STATUT_CHOICES = [
        ('BROUILLON', 'Brouillon'),
        ('VALIDEE_ETABLISSEMENT', 'Validee par l\'etablissement'),
        ('CONTROLEE_DP', 'Controlee par la DP'),
        ('CONTROLEE_ACADEMIE', 'Controlee par l\'academie'),
    ]

    etablissement = models.ForeignKey(Etablissement, on_delete=models.CASCADE, related_name='saisies_consommation')
    compteur = models.ForeignKey(Compteur, on_delete=models.CASCADE, related_name='saisies_consommation')
    annee = models.PositiveIntegerField()
    mois = models.PositiveSmallIntegerField()
    ancien_index = models.PositiveIntegerField()
    nouvel_index = models.PositiveIntegerField()
    quantite_consommee = models.PositiveIntegerField(default=0, editable=False)
    tarif_unitaire = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    montant_theorique = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'), editable=False)
    montant_fournisseur = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    ecart_montant = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'), editable=False)
    taux_ecart = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.00'), editable=False)
    statut_saisie = models.CharField(max_length=30, choices=STATUT_CHOICES, default='BROUILLON')
    saisi_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='saisies_consommation')
    date_saisie = models.DateTimeField(auto_now_add=True)
    observation = models.TextField(blank=True)

    class Meta:
        ordering = ['-annee', '-mois', '-date_saisie']
        constraints = [
            models.UniqueConstraint(
                fields=['compteur', 'annee', 'mois'],
                name='unique_saisie_mensuelle_par_compteur',
            ),
        ]

    def _recalculate(self):
        quantite = self.nouvel_index - self.ancien_index
        self.quantite_consommee = quantite
        self.montant_theorique = (Decimal(quantite) * self.tarif_unitaire).quantize(Decimal('0.01'))
        self.ecart_montant = (self.montant_fournisseur - self.montant_theorique).quantize(Decimal('0.01'))
        if self.montant_theorique > 0:
            self.taux_ecart = (abs(self.ecart_montant) / self.montant_theorique * Decimal('100')).quantize(Decimal('0.01'))
        else:
            self.taux_ecart = Decimal('0.00')

    def clean(self):
        super().clean()
        errors = {}

        if self.mois and not 1 <= self.mois <= 12:
            errors['mois'] = 'Le mois doit etre compris entre 1 et 12.'

        if self.compteur:
            if self.etablissement and self.etablissement_id != self.compteur.etablissement_id:
                errors['etablissement'] = 'L\'etablissement doit correspondre au compteur selectionne.'
            else:
                self.etablissement = self.compteur.etablissement

        if self.nouvel_index < self.ancien_index:
            errors['nouvel_index'] = 'Le nouvel index doit etre superieur ou egal a l\'ancien index.'

        self._recalculate()

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class AlerteConsommation(models.Model):
    NIVEAU_CHOICES = [
        ('INFO', 'Info'),
        ('SURVEILLANCE', 'Surveillance'),
        ('CRITIQUE', 'Critique'),
    ]

    TYPE_CHOICES = [
        ('ECART_FACTURATION', 'Ecart de facturation'),
        ('ABSENCE_SAISIE', 'Absence de saisie'),
        ('INDEX_INCOHERENT', 'Index incoherent'),
    ]

    etablissement = models.ForeignKey(Etablissement, on_delete=models.CASCADE, related_name='alertes_consommation')
    direction_provinciale = models.ForeignKey(DirectionProvinciale, on_delete=models.CASCADE, related_name='alertes_consommation', null=True, blank=True)
    academie = models.ForeignKey(Academie, on_delete=models.CASCADE, related_name='alertes_consommation', null=True, blank=True)
    compteur = models.ForeignKey(Compteur, on_delete=models.CASCADE, related_name='alertes_consommation', null=True, blank=True)
    saisie_consommation = models.ForeignKey(SaisieConsommationMensuelle, on_delete=models.CASCADE, related_name='alertes', null=True, blank=True)
    niveau_alerte = models.CharField(max_length=20, choices=NIVEAU_CHOICES)
    type_alerte = models.CharField(max_length=30, choices=TYPE_CHOICES)
    message = models.TextField()
    traitee = models.BooleanField(default=False)
    traitee_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='alertes_traitees')
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_creation']

    def clean(self):
        super().clean()
        errors = {}

        if self.saisie_consommation:
            if self.compteur and self.compteur_id != self.saisie_consommation.compteur_id:
                errors['compteur'] = 'Le compteur doit correspondre a la saisie de consommation.'
            else:
                self.compteur = self.saisie_consommation.compteur

            if self.etablissement and self.etablissement_id != self.saisie_consommation.etablissement_id:
                errors['etablissement'] = 'L\'etablissement doit correspondre a la saisie de consommation.'
            else:
                self.etablissement = self.saisie_consommation.etablissement

        if self.compteur and not self.etablissement:
            self.etablissement = self.compteur.etablissement

        if self.etablissement:
            if self.direction_provinciale and self.direction_provinciale_id != self.etablissement.direction_provinciale_id:
                errors['direction_provinciale'] = 'La direction provinciale doit correspondre a celle de l\'etablissement.'
            else:
                self.direction_provinciale = self.etablissement.direction_provinciale

            academie = self.etablissement.academie
            if not academie and self.etablissement.direction_provinciale:
                academie = self.etablissement.direction_provinciale.academie

            if self.academie and academie and self.academie_id != academie.id:
                errors['academie'] = 'L\'academie doit correspondre a celle de l\'etablissement.'
            else:
                self.academie = academie

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

class Facture(models.Model):
    TYPE_CHOICES = [('EAU', 'Eau'), ('ELECTRICITE', 'Électricité')]
    STATUT_CHOICES = [
        ('PAYEE', 'Payée'),
        ('EN_ATTENTE', 'En attente'),
        ('EN_RETARD', 'En retard'),
    ]
    etablissement = models.ForeignKey(Etablissement, on_delete=models.CASCADE)
    compteur = models.ForeignKey(Compteur, on_delete=models.SET_NULL, null=True, blank=True, related_name='factures')
    type_facture = models.CharField(max_length=15, choices=TYPE_CHOICES)
    reference = models.CharField(max_length=100, unique=True)
    numero_contrat = models.CharField(max_length=100, null=True, blank=True)
    date_emission = models.DateField()
    date_echeance = models.DateField()
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    statut = models.CharField(max_length=15, choices=STATUT_CHOICES, default='EN_ATTENTE')
    cree_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_emission', '-date_creation']

    def clean(self):
        super().clean()
        errors = {}

        if self.compteur:
            if self.etablissement_id and self.etablissement_id != self.compteur.etablissement_id:
                errors['etablissement'] = 'L\'etablissement doit correspondre au compteur selectionne.'
            else:
                self.etablissement = self.compteur.etablissement

            if self.type_facture and self.type_facture != self.compteur.type_compteur:
                errors['type_facture'] = 'Le type de facture doit correspondre au type du compteur.'

            if not self.numero_contrat:
                self.numero_contrat = self.compteur.numero_contrat

        if self.date_echeance and self.date_emission and self.date_echeance < self.date_emission:
            errors['date_echeance'] = "La date d'echeance doit etre posterieure ou egale a la date d'emission."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.type_facture} - {self.reference}"
