# Architecture cible: Roles, perimetres et consommation

## 1. Objectif

Faire evoluer la plateforme pour gerer:

- les utilisateurs Academie
- les utilisateurs DP / Direction Provinciale
- les utilisateurs Etablissement

et transformer le domaine facture en un domaine plus large de suivi de consommation eau/electricite par etablissement, tout en conservant le suivi des factures fournisseur (payee, impayee, en retard).

## 2. Niveaux d'utilisateurs

### 2.1 Academie

Les utilisateurs Academie ont une vision globale sur toutes les DP et tous les etablissements rattaches a l'academie.

Roles metiers deja presents ou a conserver:

- `ADMIN`
- `RESP_FIN`
- `RESP_INFO`
- `RESP_AUTO`

Responsabilites:

- supervision globale
- consolidation des consommations
- controle des ecarts entre consommation theorique et facture fournisseur
- traitement des alertes
- pilotage des parcs et des couts

### 2.2 DP / Direction Provinciale

Les utilisateurs DP ont une vision uniquement sur les etablissements rattaches a leur DP.

Roles proposes:

- `DP_RESP_FIN`
- `DP_RESP_INFO`
- `DP_RESP_AUTO`

Responsabilites:

- consulter la consommation des etablissements de leur perimetre
- voir quels etablissements ont saisi ou non leur consommation mensuelle
- voir les alertes de leur perimetre
- effectuer des relances et du controle de proximite

### 2.3 Etablissement

Les utilisateurs Etablissement ne voient que leur propre etablissement.

Roles proposes:

- `ETAB_RESP_CONSO`

Responsabilites:

- saisir les index eau et electricite
- consulter leur historique de consommation
- consulter les factures associees a leur etablissement
- suivre les alertes les concernant

## 3. Hierarchie administrative

La base doit exprimer une hierarchie administrative explicite:

- Academie
  - DP / Direction Provinciale
    - Commune
      - Etablissement

## 4. Modeles Django cibles

### 4.1 Academie

Champs proposes:

- `code`
- `nom`

Contraintes:

- `code` unique

### 4.2 DirectionProvinciale

Champs proposes:

- `code`
- `nom`
- `academie` (FK vers Academie)

Contraintes:

- `code` unique

### 4.3 Commune

Champs proposes:

- `nom`
- `direction_provinciale` (FK vers DirectionProvinciale)

### 4.4 Etablissement

Le modele actuel `Etablissement` dans [factures/models.py](factures/models.py) doit etre enrichi.

Champs cibles:

- `identifiant_unique`
- `nom`
- `academie` (FK vers Academie) ou derive via DP
- `direction_provinciale` (FK vers DirectionProvinciale)
- `commune` (FK vers Commune)
- `cycle` avec choix:
  - `PRIMAIRE`
  - `COLLEGE`
  - `LYCEE`
- `adresse` optionnel
- `ville` optionnel
- `actif` booleen

Contraintes:

- `identifiant_unique` unique

Remarque:

Le champ `direction_provinciale` est important pour les filtres metiers et les droits de consultation.

### 4.5 Utilisateur

Le modele utilisateur dans [accounts/models.py](accounts/models.py) doit etre etendu avec le perimetre d'appartenance.

Champs proposes:

- `role`
- `niveau_acces` avec choix:
  - `ACADEMIE`
  - `DP`
  - `ETABLISSEMENT`
- `academie` (nullable)
- `direction_provinciale` (nullable)
- `etablissement` (nullable)

Regles:

- un utilisateur Academie reference une Academie
- un utilisateur DP reference une DirectionProvinciale
- un utilisateur Etablissement reference un Etablissement
- on doit valider la coherence entre `niveau_acces` et les FK renseignees

## 5. Domaine Consommation

Le domaine facture doit etre complete par un nouveau domaine de consommation mensuelle.

### 5.1 Compteur

Un etablissement peut avoir plusieurs compteurs. Il faut donc un modele de compteur distinct.

Champs proposes:

- `etablissement` (FK)
- `type_compteur`:
  - `EAU`
  - `ELECTRICITE`
- `numero_contrat`
- `code_compteur` ou `identifiant_compteur`
- `libelle`
- `actif`

Contraintes:

- unicite sur `numero_contrat`
  ou
- unicite sur `(etablissement, type_compteur, code_compteur)` selon la realite metier

### 5.2 SaisieConsommationMensuelle

Ce modele represente la saisie de l'etablissement.

Champs proposes:

- `etablissement` (FK)
- `compteur` (FK)
- `annee`
- `mois`
- `ancien_index`
- `nouvel_index`
- `quantite_consommee`
- `tarif_unitaire`
- `montant_theorique`
- `montant_fournisseur`
- `ecart_montant`
- `taux_ecart`
- `statut_saisie`:
  - `BROUILLON`
  - `VALIDEE_ETABLISSEMENT`
  - `CONTROLEE_DP`
  - `CONTROLEE_ACADEMIE`
- `saisi_par` (FK User)
- `date_saisie`
- `observation`

Contraintes recommandees:

- unicite sur `(compteur, annee, mois)`
- `nouvel_index >= ancien_index`

Calculs automatiques:

- `quantite_consommee = nouvel_index - ancien_index`
- `montant_theorique = quantite_consommee * tarif_unitaire`
- `ecart_montant = montant_fournisseur - montant_theorique`
- `taux_ecart = abs(ecart_montant) / montant_theorique * 100` si `montant_theorique > 0`

## 6. Domaine Facture fournisseur

Le modele `Facture` actuel peut etre conserve mais doit etre mieux rattache au contexte metier.

Champs cibles:

- `etablissement`
- `compteur` (nouveau)
- `type_facture` (`EAU`, `ELECTRICITE`)
- `reference`
- `numero_contrat`
- `date_emission`
- `date_echeance`
- `montant`
- `statut`
- `cree_par`
- `date_creation`

Objectif:

La facture fournisseur sert de piece financiere et de point de comparaison avec la consommation reelle.

## 7. Alerte metier

### 7.1 Modele AlerteConsommation

Champs proposes:

- `etablissement`
- `direction_provinciale`
- `academie`
- `compteur`
- `saisie_consommation` (FK)
- `niveau_alerte`:
  - `INFO`
  - `SURVEILLANCE`
  - `CRITIQUE`
- `type_alerte`:
  - `ECART_FACTURATION`
  - `ABSENCE_SAISIE`
  - `INDEX_INCOHERENT`
- `message`
- `traitee` (booleen)
- `traitee_par` (FK User, nullable)
- `date_creation`

### 7.2 Regles de declenchement

Exemples:

- si `taux_ecart > 10%` -> alerte `SURVEILLANCE`
- si `taux_ecart > 20%` -> alerte `CRITIQUE`
- si `nouvel_index < ancien_index` -> alerte `CRITIQUE`
- si aucun releve n'est saisi pour un compteur a la fin du mois -> alerte `ABSENCE_SAISIE`

## 8. Regles d'acces

### 8.1 Academie

Peut voir:

- toutes les DP
- tous les etablissements
- toutes les consommations
- toutes les factures
- toutes les alertes

### 8.2 DP

Peut voir uniquement:

- sa DP
- les communes de sa DP
- les etablissements de sa DP
- les saisies de consommation de sa DP
- les factures de sa DP
- les alertes de sa DP

### 8.3 Etablissement

Peut voir uniquement:

- son etablissement
- ses compteurs
- ses consommations
- ses factures
- ses alertes

Ne peut pas voir les donnees des autres etablissements.

## 9. Ecrans cibles

### 9.1 Academie

- dashboard global
- vue consolidee par DP
- vue consolidee par etablissement
- liste des alertes
- suivi de la saisie manquante

### 9.2 DP

- dashboard DP
- liste des etablissements de la DP
- statut de saisie par etablissement
- alertes de la DP

### 9.3 Etablissement

- tableau de saisie mensuelle eau/electricite
- historique des index
- comparaison theorique vs facture fournisseur
- affichage des alertes locales

## 10. Strategie de migration recommandee

### Etape 1

Enrichir `Etablissement` avec:

- `identifiant_unique`
- `direction_provinciale`
- `commune`
- `cycle`

### Etape 2

Etendre `User` avec le perimetre administratif:

- `niveau_acces`
- `academie`
- `direction_provinciale`
- `etablissement`

### Etape 3

Creer le modele `Compteur`.

### Etape 4

Creer le modele `SaisieConsommationMensuelle`.

### Etape 5

Relier `Facture` a `Compteur` et ajouter `numero_contrat`.

### Etape 6

Creer le modele `AlerteConsommation`.

## 11. Impact sur l'existant

Le module facture actuel ne doit pas etre supprime.

Il doit evoluer vers 2 vues complementaires:

1. Vue detaillee des factures
- filtres payee / impayee / retard
- filtre par etablissement
- filtre par type eau / electricite

2. Vue consommation par etablissement
- calcul theorique
- montant fournisseur
- ecart
- alertes

## 12. Decision de conception recommandee

Decision recommandee:

- conserver `Facture` comme objet financier
- creer `Compteur` et `SaisieConsommationMensuelle` comme objets metiers de consommation
- faire porter les droits d'acces a la fois par role et par perimetre administratif

Cela evite de melanger:

- la saisie metier par l'etablissement
- le controle intermediaire par la DP
- la supervision financiere et technique par l'academie

## 13. Prochaine etape de developpement

Quand on passera au code, l'ordre recommande est:

1. enrichir `Etablissement`
2. enrichir `User`
3. creer `Compteur`
4. creer `SaisieConsommationMensuelle`
5. ajouter les permissions par perimetre
6. adapter l'interface facture vers la logique etablissement + consommation
