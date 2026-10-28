# Script de téléchargement pour récupérer les données - ça marche chez moi (Caro)


"""Télécharge et décompresse le corpus SICK dans data/ (non versionné)."""
import pathlib
import urllib.request
import zipfile

URL = "https://zenodo.org/records/2787612/files/SICK.zip?download=1"
# Page du corpus (si l'URL directe change) : https://zenodo.org/record/2787612

dest = pathlib.Path("data")
dest.mkdir(exist_ok=True)
zip_path = dest / "SICK.zip"

if not zip_path.exists():
    print("Téléchargement de SICK")
    urllib.request.urlretrieve(URL, zip_path)
with zipfile.ZipFile(zip_path) as z:
    z.extractall(dest)

print("Fichiers extraits :", sorted(p.name for p in dest.iterdir()))
if not (dest / "SICK.txt").exists():
    print("ATTENTION : data/SICK.txt est introuvable, vérifier le contenu de l'archive.")
