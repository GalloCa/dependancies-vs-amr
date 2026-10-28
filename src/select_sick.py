"""Sélection de paires actif/passif dans SICK (paraphrases = implication mutuelle).

Usage :
  1. Télécharger et décompresser SICK.zip (https://zenodo.org/record/2787612) ;
     le fichier utile est SICK.txt (séparateur : tabulation).
  2. python src/select_sick.py data/SICK.txt 60   # 60 paires, graine fixée
     (à lancer depuis la racine du dépôt ; écrit selection/sick_selection_regenerated.tsv,
      sans toucher à la sélection figée selection/sick_selection.tsv)

Filtres, appliqués dans cet ordre (le nombre de paires restantes est affiché) :
  1. implication mutuelle : A_entails_B ET B_entails_A (= paraphrase selon SICK) ;
  2. exactement une des deux phrases a un sujet passif (nsubjpass, spaCy) ;
  3. MÊME VERBE : le verbe passivé a le même lemme que le verbe actif de l'autre
     phrase (on ne garde que de vraies alternances de voix, sans changement de lexique) ;
  4. déduplication : une seule paire par phrase d'origine SICK, on écarte les
     quasi-doublons (recouvrement des lemmes de contenu >= DUP_THRESHOLD) et on
     limite à MAX_PER_VERB paires par verbe.
Le tirage est aléatoire mais reproductible (SEED) et se fait AVANT de regarder
les résultats des systèmes, pour ne pas choisir les paires qui nous arrangent.
"""
import csv
import random
import sys

import spacy

SEED = 42
DUP_THRESHOLD = 0.7
MAX_PER_VERB = 4      # au plus 4 paires par verbe, pour ne pas laisser 4-5 verbes dominer
nlp = spacy.load("en_core_web_sm")


def norm(lemma):
    """Le lemmatiseur de spaCy se trompe parfois (riding -> « rid », ridden -> « ride »).
    On neutralise le -e final pour que « rid » et « ride » soient comparables."""
    lemma = lemma.lower()
    return lemma[:-1] if lemma.endswith("e") and len(lemma) > 3 else lemma


def passive_verbs(doc):
    """Lemmes des verbes qui ont un sujet passif."""
    return {norm(t.head.lemma_) for t in doc if t.dep_ == "nsubjpass"}


def active_verbs(doc):
    """Lemmes des verbes sans sujet passif (formes actives)."""
    passive_heads = {t.head.i for t in doc if t.dep_ == "nsubjpass"}
    return {norm(t.lemma_) for t in doc if t.pos_ == "VERB" and t.i not in passive_heads}


def same_verb_voice_alternation(a, b):
    """Une phrase est passive, l'autre active, avec le même verbe."""
    pa, pb = passive_verbs(a), passive_verbs(b)
    if bool(pa) == bool(pb):          # les deux passives, ou aucune
        return False
    passive, active = (pa, b) if pa else (pb, a)
    return bool(passive & active_verbs(active))


def content_lemmas(a, b):
    return {norm(t.lemma_) for d in (a, b) for t in d
            if not (t.is_stop or t.is_punct or t.lemma_.lower() == "be")}


def jaccard(x, y):
    return len(x & y) / len(x | y) if x | y else 0.0


def mutual_entailment(row):
    return (row["entailment_AB"] == "A_entails_B"
            and row["entailment_BA"] == "B_entails_A")


def run(path, n):
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    step1 = [r for r in rows if mutual_entailment(r)]
    print(f"1. implication mutuelle : {len(step1)} paires")

    step2, step3 = [], []
    for r in step1:
        a, b = nlp(r["sentence_A"]), nlp(r["sentence_B"])
        if bool(passive_verbs(a)) != bool(passive_verbs(b)):
            step2.append(r)
            if same_verb_voice_alternation(a, b):
                r["_lemmas"] = content_lemmas(a, b)
                r["_verb"] = sorted(passive_verbs(a) | passive_verbs(b))[0]
                step3.append(r)
    print(f"2. une phrase au passif : {len(step2)} paires")
    print(f"3. même verbe actif/passif : {len(step3)} paires")

    random.seed(SEED)
    random.shuffle(step3)
    chosen, seen, per_verb = [], set(), {}
    for r in step3:
        if per_verb.get(r["_verb"], 0) >= MAX_PER_VERB:
            continue
        origins = {r["sentence_A_original"], r["sentence_B_original"]}
        if origins & seen:
            continue
        if any(jaccard(r["_lemmas"], c["_lemmas"]) >= DUP_THRESHOLD for c in chosen):
            continue
        seen |= origins
        per_verb[r["_verb"]] = per_verb.get(r["_verb"], 0) + 1
        chosen.append(r)
        if len(chosen) == n:
            break
    print(f"4. après déduplication, {len(chosen)} paires retenues (demandé : {n})")

    import os
    os.makedirs("selection", exist_ok=True)
    with open("selection/sick_selection_regenerated.tsv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["pair_ID", "sentence_A", "sentence_B", "relatedness_score"])
        for r in chosen:
            w.writerow([r["pair_ID"], r["sentence_A"], r["sentence_B"],
                        r.get("relatedness_score", "")])


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "data/SICK.txt"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    run(path, n)
