from django import forms
from .models import Vehicule, ConsommationCarburant, Mission


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


class MissionForm(forms.ModelForm):
    class Meta:
        model = Mission
        fields = [
            'vehicule', 'reference_om', 'date_mission', 'lieu_depart', 'destination',
            'conducteur', 'objet', 'kilometrage_depart', 'kilometrage_arrivee',
            'montant_carburant', 'observation',
        ]
        widgets = {
            'vehicule': forms.Select(attrs={'class': 'form-select'}),
            'reference_om': forms.TextInput(attrs={'class': 'form-control'}),
            'date_mission': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'lieu_depart': forms.TextInput(attrs={'class': 'form-control'}),
            'destination': forms.TextInput(attrs={'class': 'form-control'}),
            'conducteur': forms.TextInput(attrs={'class': 'form-control'}),
            'objet': forms.TextInput(attrs={'class': 'form-control'}),
            'kilometrage_depart': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'kilometrage_arrivee': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'montant_carburant': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'observation': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
