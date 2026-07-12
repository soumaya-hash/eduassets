from django import forms
from .models import Maintenance

class MaintenanceForm(forms.ModelForm):
    class Meta:
        model = Maintenance
        fields = [
            'type_cible', 'equipement', 'vehicule', 'description', 'date_intervention', 'cout', 'statut',
            'type_intervention', 'lieu', 'kilometrage_intervention', 'reference_facture',
            'pieces_remplacees', 'prochaine_echeance', 'prochain_kilometrage',
        ]
        widgets = {
            'date_intervention': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'prochaine_echeance': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # On peut masquer les champs inutiles selon le type, mais pour l'instant on laisse le choix


class MaintenanceAutomobileForm(forms.ModelForm):
    """Formulaire dédié aux interventions sur les véhicules."""

    class Meta:
        model = Maintenance
        fields = [
            'vehicule', 'type_intervention', 'description', 'date_intervention', 'lieu',
            'kilometrage_intervention', 'cout', 'reference_facture', 'pieces_remplacees',
            'prochaine_echeance', 'prochain_kilometrage', 'statut',
        ]
        widgets = {
            'vehicule': forms.Select(attrs={'class': 'form-select'}),
            'type_intervention': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date_intervention': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'lieu': forms.TextInput(attrs={'class': 'form-control'}),
            'kilometrage_intervention': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'cout': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'reference_facture': forms.TextInput(attrs={'class': 'form-control'}),
            'pieces_remplacees': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'prochaine_echeance': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'prochain_kilometrage': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
        }


class MaintenanceInformatiqueForm(forms.ModelForm):
    """Formulaire dédié aux interventions sur le matériel informatique."""

    class Meta:
        model = Maintenance
        fields = [
            'equipement', 'type_maintenance_info', 'panne_signalee', 'diagnostic',
            'description', 'date_intervention', 'prestataire', 'cout',
            'reference_facture', 'statut',
        ]
        labels = {
            'description': 'Intervention réalisée',
            'panne_signalee': 'Panne ou demande signalée',
            'diagnostic': 'Diagnostic',
            'prestataire': 'Technicien / prestataire',
        }
        widgets = {
            'equipement': forms.Select(attrs={'class': 'form-select'}),
            'type_maintenance_info': forms.Select(attrs={'class': 'form-select'}),
            'panne_signalee': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'diagnostic': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date_intervention': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'prestataire': forms.TextInput(attrs={'class': 'form-control'}),
            'cout': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'reference_facture': forms.TextInput(attrs={'class': 'form-control'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
        }
