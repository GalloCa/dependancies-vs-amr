"""
Script principal : extrait les triplets (agent, action, patient) des paires de
phrases de selection/sick_selection.tsv, en dépendances (spaCy) et en AMR
(amrlib + Penman), et écrit quatre fichiers dans output/ :
    1) sick_selection_output.tsv : une ligne par paire, avec les triplets des deux systèmes
    2) graphes_amr.txt           : les graphes AMR au format Penman
    3) trees_dep_image.html      : une page web avec le dessin de l'arbre de
                                   dépendances de chaque phrase
    4) trees_dep_text.txt        : les arbres de dépendances au format Conll

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
    """
    Lit un fichier TSV de paires de phrases, analyse chaque phrase en dépendances et
    en AMR, et écrit les quatre fichiers de sortie dans le dossier path
    (créé s'il n'existe pas).

    name : chemin du fichier TSV d'entrée
    path : dossier de sortie
    """

    data = pd.read_csv(name, sep = '\t')
    os.makedirs(path, exist_ok=True)

    file_tsv = os.path.basename(name)
    new_file_tsv = file_tsv.replace(".tsv", "_output.tsv")
    path_tsv = os.path.join(path, new_file_tsv)

    file_trees_image = "trees_dep_image.html"
    path_trees_image = os.path.join(path, file_trees_image)

    file_trees_text = "trees_dep_text.txt"
    path_trees_text = os.path.join(path, file_trees_text)

    file_graphes = "graphes_amr.txt"
    path_graphes = os.path.join(path, file_graphes)

    with open(path_tsv, mode='w', encoding='utf-8') as f1, open(path_graphes, mode='w', encoding='utf-8') as f2, open(path_trees_image, "w", encoding="utf-8") as f3, open(path_trees_text, "w", encoding="utf-8") as f4:
        f1.write(
            "pair_id\trelatedness_score\t"
            "phr_a\t"
            "dep_phr_a\tagent_dep_phr_a\taction_dep_phr_a\tpatient_dep_phr_a\t"
            # !!! DECOMMENTER POUR TESTER PHRASES NEGATIVES !!!
            # "negation_dep_phr_a\t"
            "amr_phr_a\tagent_amr_phr_a\taction_amr_phr_a\tpatient_amr_phr_a\t"
            # "negation_amr_phr_a\t"
            "phr_b\t"
            "dep_phr_b\tagent_dep_phr_b\taction_dep_phr_b\tpatient_dep_phr_b\t"
            # "negation_dep_phr_b\t"
            "amr_phr_b\tagent_amr_phr_b\taction_amr_phr_b\tpatient_amr_phr_b\n"
            # "negation_amr_phr_b\t"
        )

        f3.write(
            """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
            </head>
            <body>
            """
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
                f"{res_dep_a}\t{res_dep_a[0]}\t{res_dep_a[1]}\t{res_dep_a[2]}\t" # {res_dep_a[3]}\t" ----- !!! DECOMMENTER POUR TESTER PHRASES NEGATIVES !!!
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

            f3.write(
                "<h1>" f"id {pair_id}_A\n" "</h1>"
                "<h3>" f"{phr_a}\n" "</h3>"
                "<div>" f"{dep_a.tree_image}\n" "</div>"

                "<h1>" f"id {pair_id}_B\n" "</h1>"
                "<h3>" f"{phr_b}\n" "</h3>"
                "<div>" f"{dep_b.tree_image}\n" "</div>"
            )

            tete = "pos_du_mot\ttoken\tlemma\tétiquette\tgouverneur\tpos_du_gouv\n"

            f4.write(
                f"# sent_id = {pair_id}_A\n"
                f"# text = {phr_a}\n"
                f"{tete}"
                f"{dep_a.to_conll()}\n\n"

                f"# sent_id = {pair_id}_B\n"
                f"# text = {phr_b}\n"
                f"{tete}"
                f"{dep_b.to_conll()}\n\n"
            )

        f3.write(
        """
        </body>
        </html>
        """
        )

if __name__ == "__main__":
    file = "../selection/sick_selection.tsv"
    path = "../output"
    process(file, path)