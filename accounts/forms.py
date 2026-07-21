from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.models import Q

from factures.models import DirectionProvinciale, Etablissement

from .models import User


class CinAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label='CIN',
        max_length=20,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Saisir le CIN',
                'autocomplete': 'username',
            }
        ),
    )
    password = forms.CharField(
        label='Mot de passe',
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Saisir le mot de passe',
                'autocomplete': 'current-password',
            }
        ),
    )

    error_messages = {
        'invalid_login': 'Veuillez saisir un CIN et un mot de passe valides.',
        'inactive': 'Ce compte est inactif.',
    }


class UserManagementForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Mot de passe',
        required=False,
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}),
    )
    password2 = forms.CharField(
        label='Confirmation du mot de passe',
        required=False,
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}),
    )

    class Meta:
        model = User
        fields = [
            'cin', 'first_name', 'last_name', 'email', 'role', 'niveau_acces',
            'direction_provinciale', 'etablissement', 'is_active'
        ]
        widgets = {
            'cin': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'niveau_acces': forms.Select(attrs={'class': 'form-select'}),
            'direction_provinciale': forms.Select(attrs={'class': 'form-select'}),
            'etablissement': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        self.creator_academie = kwargs.pop('creator_academie', None)
        super().__init__(*args, **kwargs)
        self.fields['direction_provinciale'].queryset = DirectionProvinciale.objects.select_related('academie').order_by('nom')
        self.fields['etablissement'].queryset = Etablissement.objects.select_related('direction_provinciale').order_by('nom')
        self.fields['password1'].help_text = 'Laisser vide pour conserver le mot de passe actuel lors d’une modification.'

    def clean_cin(self):
        cin = User.normalize_cin(self.cleaned_data.get('cin'))
        if not cin:
            raise forms.ValidationError('Le CIN est obligatoire.')

        queryset = User.objects.filter(cin__iexact=cin)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise forms.ValidationError('Un utilisateur avec ce CIN existe déjà.')
        return cin

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if not self.instance.pk and not password1:
            self.add_error('password1', 'Le mot de passe est obligatoire à la création.')

        if password1 or password2:
            if password1 != password2:
                self.add_error('password2', 'Les deux mots de passe ne correspondent pas.')
            else:
                try:
                    validate_password(password1, self.instance)
                except ValidationError as exc:
                    self.add_error('password1', exc)

        # L'académie n'est pas choisie dans le formulaire : elle est définie
        # automatiquement pour les comptes Académie, ou déduite de la DP / de
        # l'établissement par la validation du modèle.
        if cleaned_data.get('niveau_acces') == 'ACADEMIE' and not self.instance.academie_id:
            self.instance.academie = self.creator_academie
        elif cleaned_data.get('niveau_acces') in ('DP', 'ETABLISSEMENT'):
            self.instance.academie = None

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        if not user.username:
            user.username = User.build_username_from_cin(user.cin)

        password = self.cleaned_data.get('password1')
        if password:
            user.set_password(password)

        if commit:
            user.save()
        return user


class RafResponsableConsommationForm(forms.Form):
    utilisateur = forms.ModelChoiceField(
        label='Responsable consommation', queryset=User.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    def __init__(self, *args, academie, etablissement, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['utilisateur'].queryset = User.objects.filter(
            academie=academie,
            is_active=True,
        ).order_by(
            'last_name', 'first_name', 'cin'
        )


class RafImportEtablissementsForm(forms.Form):
    fichier = forms.FileField(
        label='Fichier Excel',
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx'}),
    )
    direction_provinciale = forms.ModelChoiceField(
        label='Direction provinciale', queryset=DirectionProvinciale.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    def __init__(self, *args, academie, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['direction_provinciale'].queryset = DirectionProvinciale.objects.filter(
            academie=academie
        ).order_by('nom')

    def clean_fichier(self):
        fichier = self.cleaned_data['fichier']
        if not fichier.name.lower().endswith('.xlsx'):
            raise forms.ValidationError('Le fichier doit être au format Excel (.xlsx).')
        if fichier.size > 10 * 1024 * 1024:
            raise forms.ValidationError('Le fichier ne doit pas dépasser 10 Mo.')
        return fichier
