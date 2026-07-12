# Generated manually because the local Python interpreter configured for this project is unavailable.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('automobile', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Mission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference_om', models.CharField(max_length=50, unique=True, verbose_name='Référence OM')),
                ('date_mission', models.DateField(verbose_name='Date de mission')),
                ('lieu_depart', models.CharField(max_length=150, verbose_name='Lieu de départ')),
                ('destination', models.CharField(max_length=150)),
                ('conducteur', models.CharField(max_length=150)),
                ('objet', models.CharField(blank=True, max_length=250, verbose_name='Objet de la mission')),
                ('kilometrage_depart', models.PositiveIntegerField(verbose_name='Kilométrage au départ')),
                ('kilometrage_arrivee', models.PositiveIntegerField(verbose_name="Kilométrage à l'arrivée")),
                ('distance_parcourue', models.PositiveIntegerField(default=0, editable=False)),
                ('montant_carburant', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Montant du carburant (DH)')),
                ('observation', models.TextField(blank=True)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('cree_par', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('vehicule', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='missions', to='automobile.vehicule')),
            ],
            options={
                'verbose_name': 'mission',
                'verbose_name_plural': 'missions',
                'ordering': ['-date_mission', '-id'],
            },
        ),
    ]
