from django import forms
from .models import Maintenance

class MaintenanceForm(forms.ModelForm):
    class Meta:
        model = Maintenance
        fields = ['type_cible', 'equipement', 'vehicule', 'description', 'date_intervention', 'cout', 'statut']
        widgets = {
            'date_intervention': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # On peut masquer les champs inutiles selon le type, mais pour l'instant on laisse le choix