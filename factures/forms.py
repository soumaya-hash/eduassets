from django import forms
from .models import Facture, SaisieConsommationMensuelle, Compteur

class FactureForm(forms.ModelForm):
    fournisseur = forms.ChoiceField(
        label='Compteur',
        choices=Facture.FOURNISSEUR_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    date_emission = forms.DateField(
        input_formats=['%m/%d/%Y', '%Y-%m-%d'],
        widget=forms.DateInput(attrs={'placeholder': 'mm/dd/yyyy', 'type': 'text'})
    )
    date_echeance = forms.DateField(
        input_formats=['%m/%d/%Y', '%Y-%m-%d'],
        widget=forms.DateInput(attrs={'placeholder': 'mm/dd/yyyy', 'type': 'text'})
    )

    class Meta:
        model = Facture
        fields = [
            'etablissement', 'fournisseur', 'type_facture', 'reference',
            'numero_contrat', 'date_emission', 'date_echeance', 'montant', 'statut'
        ]


class SaisieConsommationMensuelleForm(forms.ModelForm):
    annee = forms.IntegerField(
        min_value=2000,
        max_value=2100,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    mois = forms.IntegerField(
        min_value=1,
        max_value=12,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    compteur = forms.ModelChoiceField(
        queryset=Compteur.objects.select_related('etablissement'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = SaisieConsommationMensuelle
        fields = [
            'compteur', 'annee', 'mois', 'ancien_index', 'nouvel_index',
            'tarif_unitaire', 'montant_fournisseur', 'observation'
        ]
        widgets = {
            'ancien_index': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'nouvel_index': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'tarif_unitaire': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'montant_fournisseur': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'observation': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        etablissement = kwargs.pop('etablissement', None)
        super().__init__(*args, **kwargs)
        if etablissement is not None:
            self.fields['compteur'].queryset = Compteur.objects.filter(etablissement=etablissement).order_by('type_compteur', 'libelle')


class CompteurForm(forms.ModelForm):
    """Formulaire de création d'un compteur par son établissement."""

    class Meta:
        model = Compteur
        fields = ['fournisseur', 'type_compteur', 'libelle', 'numero_contrat', 'code_compteur']
        widgets = {
            'fournisseur': forms.Select(attrs={'class': 'form-select'}),
            'type_compteur': forms.Select(attrs={'class': 'form-select'}),
            'libelle': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_contrat': forms.TextInput(attrs={'class': 'form-control'}),
            'code_compteur': forms.TextInput(attrs={'class': 'form-control'}),
        }
