# Generated manually because the local Python virtual environment is unavailable.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('factures', '0003_alter_academie_options_alter_commune_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='commune',
            name='code',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='etablissement',
            name='code_milieu',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='etablissement',
            name='etablissement_rattachement',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='etablissements_rattaches',
                to='factures.etablissement',
            ),
        ),
        migrations.AddField(
            model_name='etablissement',
            name='nom_arabe',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='etablissement',
            name='type_etablissement',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='commune',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='commune',
            constraint=models.UniqueConstraint(
                fields=('nom', 'direction_provinciale'),
                name='unique_commune_nom_par_dp',
            ),
        ),
        migrations.AddConstraint(
            model_name='commune',
            constraint=models.UniqueConstraint(
                fields=('code', 'direction_provinciale'),
                name='unique_commune_code_par_dp',
            ),
        ),
    ]
