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


## Données

Corpus SICK (Marelli et al., 2014), non versionné : il est téléchargé par un script.

```
python scripts/download_data.py          # crée data/SICK.txt
```

## Sélection des 60 paires de test

La sélection est **figée** dans `selection/sick_selection.tsv` : c'est ce fichier qui sert de
référence pour toutes les expériences. Elle a été produite par `scripts/select_sick.py` avec les
filtres suivants (compteurs sur le corpus complet, 9 840 paires) :

| Étape | Filtre | Paires restantes |
|---|---|---|
| 1 | Implication mutuelle (A_entails_B et B_entails_A) | 1 300 |
| 2 | Exactement une phrase au passif (`nsubjpass`) | 331 |
| 3 | Même verbe (lemme) à l'actif et au passif | 307 |
| 4 | Déduplication (une paire par phrase d'origine, quasi-doublons écartés, max. 4 paires par verbe) puis tirage de 60 (graine 42) | 60 |

Pour regénérer la sélection (attention => le résultat peut différer légèrement selon la version de spaCy) :

```
python scripts/select_sick.py data/SICK.txt 60
```

Produit un nouveau fichier `selection/sick_selection_regenerated.tsv` 

## Structure du dépôt

```
README.md
scripts/             scripts + requirements
selection/           sélection figée des paires de test
data/                corpus téléchargé (non versionné)
output/              sorties des expériences
```


## Analyse en dépendances et en AMR

Cette partie lit les paires de phrases de `selection/sick_selection.tsv`. Pour chaque phrase, elle extrait un triplet (agent, action, patient) de deux façons : avec des règles sur l'arbre de dépendances (spaCy) et avec des règles équivalentes sur le graphe AMR (amrlib + Penman). Les résultats, ainsi que les arbres et les graphes de chaque phrase, sont écrits dans le dossier `output/`.

### Fichiers

Dossier `scripts` :

| Fichier | Rôle |
|---|---|
| `download_data.py` | télécharge le corpus SICK dans `data/` |
| `select_sick.py` | regénère une sélection de paires actif/passif à partir de SICK |
| `main.py` | lit le TSV d'entrée, lance les deux analyses et écrit les fichiers de sortie |
| `dependencies.py` | classe `Dependencies` : analyse en dépendances, règles d'extraction, dessin et format Conll de l'arbre |
| `amr.py` | classe `AMR` : analyse AMR et règles d'extraction |
| `visualise_amr.py` | (optionnel) dessine les graphes AMR de `output/graphes_amr.txt` dans une page HTML |

### Installation

1. Bibliothèques Python (depuis la racine du dépôt) :
   ```bash
   pip install -r scripts/requirements.txt
   ```
2. Modèle spaCy :
   ```bash
   python -m spacy download en_core_web_sm
   ```
3. Modèle AMR : on utilise `parse_xfm_bart_base` (environ 500 Mo), plus petit et plus rapide que la version `large`.
   1. Télécharger le fichier `.tar.gz` : https://github.com/bjascob/amrlib-models/releases/download/parse_xfm_bart_base-v0_1_0/model_parse_xfm_bart_base-v0_1_0.tar.gz (sous Windows, le plus simple est de passer par le navigateur).
   2. Trouver le dossier d'installation d'AMRlib :
      ```bash
      pip show amrlib
      ```
      La ligne `Location` donne un chemin ; le dossier d'AMRlib est `<Location>/amrlib`.
   3. Décompresser le modèle dans `<Location>/amrlib/data/` (créer le dossier `data` s'il n'existe pas) :
      ```bash
      tar -xzf model_parse_xfm_bart_base-v0_1_0.tar.gz -C <Location>/amrlib/data
      ```
      La commande `tar` fonctionne aussi dans PowerShell sous Windows 10 et 11.
   4. Renommer le dossier obtenu en `model_stog`. Le fichier `amrlib_meta.json` doit se trouver directement dans `model_stog`.

### Lancement

Depuis le dossier `scripts` :

```bash
cd scripts
python main.py
```

Le fichier d'entrée et le dossier de sortie sont définis en bas de `main.py`. Sans GPU, le parsing AMR est lent : comptez quelques minutes pour les 120 phrases.

### Visualisation des graphes AMR (optionnel)

Le script `visualise_amr.py` dessine les graphes AMR produits par `main.py` et les rassemble dans une page web. Il est séparé de `main.py` car il demande d'installer un programme en plus, Graphviz. Si Graphviz n'est pas installé, `main.py` fonctionne quand même. Les arbres de dépendances, eux, sont dessinés directement par `main.py` (avec displaCy), sans installation supplémentaire.

**Installation** : installer le programme Graphviz : https://graphviz.org/download/
Sous Windows, cocher l'option qui ajoute Graphviz au `PATH` pendant l'installation. Pour vérifier que c'est bon, la commande suivante doit afficher un numéro de version :

```bash
dot -V
```

La bibliothèque Python `graphviz` est déjà dans `requirements.txt`.

**Lancement** : depuis le dossier `scripts`, après avoir lancé `main.py` :

```bash
python visualise_amr.py
```

Le script lit `output/graphes_amr.txt` et écrit `output/graphes_amr_image.html`. Si le message `ExecutableNotFound` apparaît, c'est que le programme Graphviz n'est pas installé ou n'est pas dans le `PATH`.

### Fichiers produits

**`output/sick_selection_output.tsv`** : une ligne par paire de phrases.

- `pair_id`, `relatedness_score` : identifiant et score de proximité repris de SICK
- `phr_a` : la phrase A
- `dep_phr_a` : le triplet complet en dépendances, puis `agent_dep_phr_a`, `action_dep_phr_a`, `patient_dep_phr_a` : ses éléments séparés
- `amr_phr_a`, `agent_amr_phr_a`, `action_amr_phr_a`, `patient_amr_phr_a` : la même chose en AMR
- les mêmes colonnes pour la phrase B (`phr_b`, `dep_phr_b`, etc.)

`None` signifie que les règles n'ont pas trouvé l'élément (par exemple, pas de patient). Attention : relu avec pandas, `None` devient une case vide (`NaN`), et `NaN == NaN` vaut `False`.

**`output/graphes_amr.txt`** : les 120 graphes AMR au format Penman, séparés par une ligne vide. Chaque graphe est précédé d'une ligne `# ::id <pair_ID>_A` (ou `_B`) qui permet de le retrouver, et d'une ligne `# ::snt` avec la phrase. Le fichier peut être relu avec `penman.load(...)`.

**`output/trees_dep_image.html`** : une page web avec, pour chaque phrase, son identifiant, la phrase et le dessin de son arbre de dépendances (displaCy). Elle s'ouvre dans un navigateur.

**`output/trees_dep_text.txt`** : les 120 arbres de dépendances au format Conll. Chaque phrase commence par deux lignes de commentaire, `# sent_id = <pair_ID>_A` (ou `_B`) et `# text = <phrase>`, suivies d'une ligne avec le nom des colonnes, puis d'une ligne par token : position du token, token, lemme, étiquette, gouverneur, position du gouverneur. Les phrases sont séparées par une ligne vide.

**`output/graphes_amr_image.html`** (seulement si on lance `visualise_amr.py`) : une page web avec, pour chaque phrase, son identifiant, la phrase et le dessin de son graphe AMR.

### Règles d'extraction

| Élément | Dépendances | AMR |
|---|---|---|
| **Action** | lemme de la racine (`ROOT`) | concept de la racine du graphe |
| **Agent**, actif | enfant `nsubj` de la racine | concept de l'enfant `:ARG0` de la racine |
| **Agent**, passif | enfant `pobj` de l'enfant `agent` | idem (`:ARG0`) |
| **Patient**, actif | enfant `dobj` de la racine | concept de l'enfant `:ARG1` de la racine |
| **Patient**, passif | enfant `nsubjpass` de la racine | idem (`:ARG1`) |
| **Patient**, option désactivée | — | concept de l'enfant `:ARG2`, s'il n'y a pas de `:ARG1` |
| **Négation**, option désactivée | enfant `neg` de la racine | attribut `:polarity -` de la racine |
| **Normalisation** | lemmes en minuscules | concepts en minuscules, sans numéro de sens (`play-11` → `play`) |

Côté spaCy, une phrase est traitée comme passive si la racine a un enfant `nsubjpass`. Côté AMR, il n'y a pas de cas particulier pour le passif.

### Options désactivées : négation et `:ARG2`

Deux règles sont écrites dans le code mais désactivées (en commentaire). Pour les activer, il faut enlever les `#` aux endroits marqués `!!! DECOMMENTER ... !!!`.

**`:ARG2` comme patient (AMR seulement).** Le parseur AMR met parfois le patient en `:ARG2` au lieu de `:ARG1` (par exemple *play* avec un instrument). Avec cette option, si le graphe n'a pas de `:ARG1`, l'enfant `:ARG2` est pris comme patient. Les lignes sont dans `amr.py`, méthode `triplet_amr`. Attention : `:ARG2` ne désigne pas le patient pour tous les verbes (pour *give-01*, c'est celui qui reçoit), et cette règle n'existe que côté AMR. Il vaut mieux comparer les résultats avec et sans cette option.

**Négation.** Ajoute un 4ᵉ élément au triplet : `True` si la phrase est négative, `False` sinon. Il faut décommenter dans **les trois fichiers à la fois** :
- `dependencies.py`, méthode `triplet_dep` : la recherche de l'enfant `neg`, et `negation` dans le `return` ;
- `amr.py`, méthode `triplet_amr` : la recherche de `:polarity -`, et `negation` dans le `return` ;
- `main.py` : les quatre colonnes `negation_...` de l'en-tête et les quatre valeurs `[3]` des lignes de données. Vérifier ensuite que chaque morceau de ligne se termine par `\t`, sauf le dernier, qui se termine par `\n`.

Si un seul fichier est modifié, les colonnes du TSV seront décalées, ou le script s'arrêtera avec une `IndexError`.


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