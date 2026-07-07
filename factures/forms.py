from django import forms
from .models import Facture

class FactureForm(forms.ModelForm):
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
            'etablissement', 'type_facture', 'reference',
            'date_emission', 'date_echeance', 'montant', 'statut'
        ]