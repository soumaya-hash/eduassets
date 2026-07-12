# Import des établissements — Province de Fahs-Anjra

La commande `importer_etablissements` charge l’échantillon Excel dans la hiérarchie :

- Académie
- Direction provinciale `227 — Province de Fahs-Anjra`
- Communes
- Établissements

Tous les types présents dans la source sont conservés (`Public`, `NS`, `ENF`, `Prive`, `PART`).
Ils restent filtrables grâce au champ `type_etablissement`; aucune donnée officielle n’est écartée.

Les codes sont les clés d’import :

- `cd_com` pour les communes
- `CD_ETAB` pour les établissements
- `CD_etabr` pour le rattachement d’un établissement satellite à son établissement principal

L’import est idempotent : relancer la commande met à jour les mêmes enregistrements au lieu de les dupliquer.

## Avant l’import

1. Installer les dépendances Python du projet, y compris `openpyxl`.
2. Appliquer les migrations.
3. Remplacer `<CODE_ACADEMIE>` et `<NOM_ACADEMIE>` par les informations officielles de l’académie concernée.

## Validation sans écriture

```powershell
python manage.py importer_etablissements `
  --fichier "C:\Users\souma\Desktop\Requête1.xlsx" `
  --academie-code "<CODE_ACADEMIE>" `
  --academie-nom "<NOM_ACADEMIE>"
```

## Import effectif

Après avoir lu le rapport de validation, relancer la même commande avec `--appliquer` :

```powershell
python manage.py importer_etablissements `
  --fichier "C:\Users\souma\Desktop\Requête1.xlsx" `
  --academie-code "<CODE_ACADEMIE>" `
  --academie-nom "<NOM_ACADEMIE>" `
  --appliquer
```

La commande signale les codes de rattachement absents du fichier au lieu de créer des relations erronées.
