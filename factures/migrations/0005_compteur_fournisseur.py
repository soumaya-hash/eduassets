from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('factures', '0004_commune_code_etablissement_source_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='compteur',
            name='fournisseur',
            field=models.CharField(
                choices=[('AMENDIS', 'Amendis'), ('SRM', 'SRM')],
                default='AMENDIS',
                max_length=10,
            ),
        ),
    ]
