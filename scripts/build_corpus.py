"""Commentaire utilisation à rajouter
!!!! ATTENTION si on régénère un corpus, pas forcément le même qu'on aura
"""

import csv
import os
import random
import sys 
import spacy

# CONSTANTES - Maybe un fichiers à part si beaucoup de constantes (?)
SEED = 2026
N_RICH = 12
MAX_PER_VERB = 4      # choix => au plus 4 paires par verbe, pour ne pas laisser 4-5 verbes dominer le corpus
DUP_THRESHOLD = 0.7
PREP_OBJ = {"at", "on", "into", "over", "in", "to", "with", "from"}
nlp = spacy.load("en_core_web_sm")


def norm(lemma):
    """Le lemmatiseur de spaCy peut se tromper (riding -> « rid », ridden -> « ride »).
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

# Categories = utiles pour former le corpus et classer en fonction de si phrases simple / relative / coordination / etc ...
def passive_info(a, b):
    """Renvoie : côté passif 'A'/'B', doc passif, doc actif, lemme du verbe passivé"""
    for side, d, other in (("A", a, b), ("B", b, a)):
        heads = [t.head for t in d if t.dep_ == "nsubjpass"]
        if heads:
            return side, d, other, heads[0].lemma_.lower()
    return None, None, None, None

def noun_lemmas(doc):
    return {t.lemma_.lower() for t in doc if t.pos_ in ("NOUN", "PROPN")}

def categories(a,b):
    """Renvoie : côté passif, lemme du verbe passivé, liste de catégories"""
    side, passive, active, verb = passive_info(a, b)
    cats = []
    if noun_lemmas(a) != noun_lemmas(b):
        cats.append("voc_different")
    if passive is not None and not any(t.dep_ == "agent" or t.text.lower() == "by" for t in passive):
        cats.append("rich_structure")
    for d in (a, b) :
        for t in d :
            if t.pos_ == "VERB" and t.lemma_.lower() == verb and any(
                c.dep_ == "dative" or (c.dep_ == "prep" and c.text.lower() == "to") for c in t.children):
                if "datif" not in cats :
                    cats.append("datif")
    if active is not None : 
        for t in active :
            if t.pos_ == "VERB" and t.lemma_.lower() == verb :
                has_dobj = any(c.dep_ in ("dobj", "obj") for c in t.children)
                if not has_dobj and any(c.dep_ == "prep" and c.text.lower() in PREP_OBJ for c in t.children):
                    cats.append("prepositional_object")
                break
    return side, verb, cats

# construction du corpus 
def run(path, n, out):
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    step1 = [r for r in rows if mutual_entailment(r)]
    print(f"On regarde si y'a implication mutuelle : {len(step1)} paires")

    step2, step3, pool = 0, 0 , []
    for r in step1:
        a, b = nlp(r["sentence_A"]), nlp(r["sentence_B"])
        if bool(passive_verbs(a)) == bool(passive_verbs(b)):
            continue
        step2 += 1
        if not same_verb_voice_alternation(a, b):
            continue
        step3 += 1
        side, verb, cats = categories(a, b)
        if {"voc_different", "sans_by"} & set(cats):
            continue
        r.update(_lemmas = content_lemmas(a, b), _verb = norm(verb), _side=side, _vraw = verb,
                _cats = cats or ["voix_simple"], _rich = "rich_structure" in cats)
        pool.append(r)
       
    print(f"Sort les phrases au passif : {step2} paires")
    print(f"Si même verbe pour actif/passif : {step3} paires")
    print(f"mêmes noms et complément en 'by' : {len(pool)} paires")

    random.seed(SEED)
    random.shuffle(pool)
    rich = [r for r in pool if r["_rich"]]
    autres = [r for r in pool if not r["_rich"]]

    chosen, seen, per_verb = [], set(), {}

    def try_add(r):
        """Ajoute la paire si pas trop proche d'une autre, et si pas trop de fois le même verbe déjà"""
        if per_verb.get(r["_verb"], 0) >= MAX_PER_VERB:
            return False
        origins = {r["sentence_A_original"], r["sentence_B_original"]}
        if origins & seen : 
            return False
        if any(jaccard(r["_lemmas"], c["_lemmas"]) >= DUP_THRESHOLD for c in chosen):
            return False
        seen.update(origins)
        per_verb[r["_verb"]] = per_verb.get(r["_verb"], 0) + 1
        chosen.append(r)
        return True

    n_rich = 0 
    for r in rich : 
        if n_rich == N_RICH:
            break
        n_rich += try_add(r)
    for r in autres + [r for r in rich if r not in chosen] :
        if len(chosen) == n:
            break
        try_add(r)
    print(f"Problème parfois phrase trop proche donc je dédupliques, {len(chosen)} paires retenues (demandé : {n})")

    
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    chosen.sort(key=lambda r : int(r["pair_ID"]))

    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["pair_ID", "sentence_A", "sentence_B", "relatedness_score", 
                    "passive_side", "verb_lemma", "categories"])
        for r in chosen:
            w.writerow([r["pair_ID"], r["sentence_A"], r["sentence_B"],
                        r.get("relatedness_score", ""), r["_side"], r["_vraw"], ";".join(r["_cats"])])
    print(f"fichier écrit")



if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "data/SICK.txt"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 80
    out = sys.argv[3] if len(sys.argv) > 3 else "selection/corpus.tsv"
    run(path, n, out)
           