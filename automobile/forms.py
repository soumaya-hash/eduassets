from django import forms
from .models import Vehicule, ConsommationCarburant


class VehiculeForm(forms.ModelForm):
    class Meta:
        model = Vehicule
        fields = ['matricule', 'marque', 'modele', 'annee', 'kilometrage', 'affectation']
        labels = {
            'affectation': "Etablissement d'affectation",
        }
        widgets = {
            'matricule': forms.TextInput(attrs={'class': 'form-control'}),
            'marque': forms.TextInput(attrs={'class': 'form-control'}),
            'modele': forms.TextInput(attrs={'class': 'form-control'}),
            'annee': forms.NumberInput(attrs={'class': 'form-control'}),
            'kilometrage': forms.NumberInput(attrs={'class': 'form-control'}),
            'affectation': forms.Select(attrs={'class': 'form-select'}),
        }


class ConsommationCarburantForm(forms.ModelForm):
    class Meta:
        model = ConsommationCarburant
        fields = ['vehicule', 'date', 'quantite_litres', 'cout']
        widgets = {
            'vehicule': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'quantite_litres': forms.NumberInput(attrs={'class': 'form-control'}),
            'cout': forms.NumberInput(attrs={'class': 'form-control'}),
        }
