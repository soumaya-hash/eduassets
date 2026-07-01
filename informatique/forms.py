from django import forms
from .models import EquipementInformatique

class EquipementForm(forms.ModelForm):
    class Meta:
        model = EquipementInformatique
        fields = [
            'numero_inventaire', 'designation', 'marque', 'modele',
            'date_acquisition', 'etablissement', 'etat'
        ]
        widgets = {
            'date_acquisition': forms.DateInput(attrs={'type': 'date'}),
        }