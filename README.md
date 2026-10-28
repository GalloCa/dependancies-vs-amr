## WIP : 

# L'AMR est-elle plus robuste que la syntaxe face aux reformulations ?

Projet du cours *Syntaxe et Sémantique* (M2 IdL, UGA, 2026).

Auteurs : Mettre nos noms ici 

## Objectif

Comparer deux systèmes de règles qui extraient un triplet (agent, action, patient) :
l'un sur les arbres de dépendances (spaCy), l'autre sur les graphes AMR (AMRlib + Penman).


**A vérifier avec le groupe si c'est bien ça**
*On mesure s'ils extraient **le même triplet** des deux phrases d'une paire à implication mutuelle
(ex. « A girl is playing a flute » / « A flute is being played by a girl »).*

*Attention : ce critère mesure la **cohérence entre deux phrases**, pas la justesse du triplet,
et « implication mutuelle » (annotation NLI de SICK) n'est pas une paraphrase stricte.*

## Installation

```
python -m venv .venv
.venv\Scripts\activate          # Windows  (macOS/Linux : source .venv/bin/activate)
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

Versions spacy utilisées : spaCy 3.8.18, modèle `en_core_web_sm` 3.8.0

## Données

Corpus SICK (Marelli et al., 2014), non versionné : il est téléchargé par un script.

```
python download_data.py          # crée data/SICK.txt
```

## Sélection des 60 paires de test

La sélection est **figée** dans `selection/sick_selection.tsv` : c'est ce fichier qui sert de
référence pour toutes les expériences. Elle a été produite par `src/select_sick.py` avec les
filtres suivants (compteurs sur le corpus complet, 9 840 paires) :

| Étape | Filtre | Paires restantes |
|---|---|---|
| 1 | Implication mutuelle (A_entails_B et B_entails_A) | 1 300 |
| 2 | Exactement une phrase au passif (`nsubjpass`) | 331 |
| 3 | Même verbe (lemme) à l'actif et au passif | 307 |
| 4 | Déduplication (une paire par phrase d'origine, quasi-doublons écartés, max. 4 paires par verbe) puis tirage de 60 (graine 42) | 60 |

Pour regénérer la sélection (attention => le résultat peut différer légèrement selon la version de spaCy) :

```
python src/select_sick.py data/SICK.txt 60
```

Produit un nouveau fichier `selection/sick_selection_regenerated.tsv` 

## Structure du dépôt

```
README.md
requirements.txt
download_data.py
src/                 scripts (sélection, systèmes spaCy et AMR, évaluation)
selection/           sélection figée des paires de test
data/                corpus téléchargé (non versionné)
results/             sorties des expériences
```

## Résultats 

***A compléter***


## Limites (à compléter)

- Une seule transformation étudiée (alternance actif/passif), sur des phrases courtes.
- Une partie des paires de SICK est construite par transformation automatique de phrases d'origine.
- 60 paires : seuls des écarts nets sont interprétables.
- Les résultats dépendent de la qualité des deux parseurs.

## Référence

Marelli et al. (2014), *A SICK cure for the evaluation of compositional distributional semantic
models*. Corpus : https://zenodo.org/record/2787612 (licence : voir la page du corpus).

spacy et amr pennman (?)
