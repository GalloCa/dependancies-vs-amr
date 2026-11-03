"""
Script qui dessine les graphes AMR produits par main.py

Ce script est optionnel. Il lit output/graphes_amr.txt (les graphes au format
Penman écrits par main.py), dessine chaque graphe avec AMRPlot (amrlib) et
Graphviz, et écrit la page web output/graphes_amr_image.html. Pour chaque
phrase, la page affiche son identifiant, la phrase et le dessin du graphe.

Usage (depuis le dossier scripts) :
    python main.py            # d'abord, pour produire output/graphes_amr.txt
    python visualise_amr.py

Prérequis : les bibliothèques Python de requirements.txt (dont graphviz) et
le programme Graphviz (https://graphviz.org/download/).
"""

import penman
import os
from amrlib.graph_processing.amr_plot import AMRPlot

html_start = """
      <!DOCTYPE html>
      <html lang="en">
      <head>
          <meta charset="UTF-8">
      </head>
      <body>
      """

html_end = """
    </body>
    </html>
    """

def visualise_amr(graph_penman):
    """
    Dessine un graphe AMR au format SVG.
    Renvoie le dessin du graphe sous forme de texte SVG (str), prêt pour une page HTML.
    Lève graphviz.ExecutableNotFound si le programme Graphviz n'est pas installé.

    graph_penman : un graphe Penman, liste renvoyée par penman.load
    """

    text = penman.encode(graph_penman)
    plot = AMRPlot(format='svg')
    plot.build_from_graph(text, debug=False)
    di_graph = plot.graph # objet Digraph de Graphviz construit par AMRPlot (image)
    image_description = di_graph.pipe(encoding='utf-8') # image transformée en texte SVG
    return image_description

def process(file, path):
    """
    Lit un fichier de graphes AMR au format Penman et écrit une page HTML
    avec le dessin de chaque graphe.

    file : chemin du fichier de graphes (ex. ../output/graphes_amr.txt) ;
           chaque graphe doit avoir les métadonnées # ::id et # ::snt
    path : dossier où écrire graphes_amr_image.html (créé s'il n'existe pas)
    """
        
    file_graphes_image = "graphes_amr_image.html"
    os.makedirs(path, exist_ok=True)
    path_graphes_image = os.path.join(path, file_graphes_image)

    with open(path_graphes_image, mode='w', encoding='utf-8') as f:
        f.write(html_start)

        data = penman.load(file) # liste
        for chunk in data:
            meta = chunk.metadata
            pair_id = meta.get('id')
            phr = meta.get('snt')

            f.write(
            "<h1>" f"id {pair_id}\n" "</h1>"
            "<h3>" f"{phr}\n" "</h3>"
            "<div>" f"{visualise_amr(chunk)}\n" "</div>"
            )

        f.write(html_end)



if __name__ == "__main__":
    file = "../output/graphes_amr.txt"
    path = "../output"
    process(file, path)