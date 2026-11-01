"""
But : ce script présente une fonction qui lit un fichier .tsv avec des phrases et crée 2 fichiers :
    1) graphes_amr.txt, avec graphes AMR pour chaque phrase
    2) sick_selection_output.tsv, avec des résultats de parsing

Usage : depuis le dossier scripts, python main.py
"""

# modules
import spacy
import amrlib
import pandas as pd
import unidecode
import os
from dependencies import Dependencies
from amr import AMR

# modelès
nlp = spacy.load("en_core_web_sm")
stog = amrlib.load_stog_model()


def process(name, path):
    data = pd.read_csv(name, sep = '\t')
    os.makedirs(path, exist_ok=True)

    file_tsv = os.path.basename(name)
    new_file_tsv = file_tsv.replace(".tsv", "_output.tsv")
    path_tsv = os.path.join(path, new_file_tsv)

    file_graphes = "graphes_amr.txt"
    path_graphes = os.path.join(path, file_graphes)

    with open(path_tsv, mode='w', encoding='utf-8') as f1, open(path_graphes, mode='w', encoding='utf-8') as f2:
        f1.write(
            "pair_id\trelatedness_score\t"
            "phr_a\t"
            "dep_phr_a\tagent_dep_phr_a\taction_dep_phr_a\tpatient_dep_phr_a\t"
            # "negation_dep_phr_a\t"
            "amr_phr_a\tagent_amr_phr_a\taction_amr_phr_a\tpatient_amr_phr_a\t"
            # "negation_amr_phr_a\t"
            "phr_b\t"
            "dep_phr_b\tagent_dep_phr_b\taction_dep_phr_b\tpatient_dep_phr_b\t"
            # "negation_dep_phr_b\t"
            "amr_phr_b\tagent_amr_phr_b\taction_amr_phr_b\tpatient_amr_phr_b\n"
            # "negation_amr_phr_b\t"
        )

        for row in data.itertuples():
            pair_id = row.pair_ID
            phr_a = row.sentence_A
            phr_b = row.sentence_B
            score = row.relatedness_score

            dep_a = Dependencies(phr_a, nlp)
            res_dep_a = dep_a.triplet_dep()
            amr_a = AMR(phr_a, stog)
            res_amr_a = amr_a.triplet_amr()

            dep_b = Dependencies(phr_b, nlp)
            res_dep_b = dep_b.triplet_dep()
            amr_b = AMR(phr_b, stog)
            res_amr_b = amr_b.triplet_amr()

            f1.write(
                f"{pair_id}\t{score}\t"
                f"{phr_a}\t"
                f"{res_dep_a}\t{res_dep_a[0]}\t{res_dep_a[1]}\t{res_dep_a[2]}\t" # {res_dep_a[3]}\t"
                f"{res_amr_a}\t{res_amr_a[0]}\t{res_amr_a[1]}\t{res_amr_a[2]}\t" # {res_amr_a[3]}\t"
                f"{phr_b}\t"
                f"{res_dep_b}\t{res_dep_b[0]}\t{res_dep_b[1]}\t{res_dep_b[2]}\t" # {res_dep_b[3]}\t"
                f"{res_amr_b}\t{res_amr_b[0]}\t{res_amr_b[1]}\t{res_amr_b[2]}\n" # {res_amr_b[3]}\n"
            )

            f2.write(
                f"# ::id {pair_id}_A\n"
                f"{amr_a.parsed_phrase}\n\n"
                f"# ::id {pair_id}_B\n"
                f"{amr_b.parsed_phrase}\n\n"
            )

if __name__ == "__main__":
    file = "../selection/sick_selection.tsv"
    path = "../output"
    process(file, path)