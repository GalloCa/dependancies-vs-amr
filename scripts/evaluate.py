"""evaluation quantitative et qualitative - stats"""

import sys
import numpy as np
import pandas as pd 
from scipy.stats import binomtest

PRONOMS_VAGUE = {"someone", "somebody", "anyone", "anybody", "something"}

def norm(lemma):
    """pour harmoniser anomalies de surface 
    ex rid vs ride
    """
    if not isinstance(lemma, str):
        return lemma
    lemma = lemma.lower().strip()
    return lemma[:-1] if lemma.endswith("e") and len(lemma) > 3 else lemma

def clean_val(val):
    """nettoyage + enlève pronoms vague pour calcul de l'invariance souple
        dans notre corpus on a que 'someone' mais ça permet une protection 
        pour réplication si autre phrase sélectionnées.
    """
    if pd.isna(val) or str(val).strip().lower() in ("none", "null", ""):
        return None
    v = str(val).strip().lower()
    return None if v in PRONOMS_VAGUE else v

def ic(arr, n_boot=10000):
    """calcule de l'intervalle de confiance à 95%"""
    means = [
        np.mean(np.random.choice(arr, size=len(arr), replace=True))
        for _ in range(n_boot)
    ]
    return np.percentile(means, 2.5) * 100, np.percentile(means, 97.5) * 100

def evaluate_pipeline(tsv_path):
    df = pd.read_csv(tsv_path, sep="\t")
    n = len(df)

    print("Test evaluate_pipeline - start")

    # eval par système - comparaison  invariance stricte et souple 
    for sys_name in ["dep" , "amr"]:
        strict_matches = []
        soft_matches = []
        couverture = []

        for _, r in df.iterrows():
            agt_a = clean_val(r[f"agent_{sys_name}_phr_a"]) # recherche agent A
            act_a = norm(clean_val(r[f"action_{sys_name}_phr_a"])) # recherche action A
            pat_a = clean_val(r[f"patient_{sys_name}_phr_a"]) # recherche patient A

            agt_b = clean_val(r[f"agent_{sys_name}_phr_b"]) # recherche agent B
            act_b = norm(clean_val(r[f"action_{sys_name}_phr_b"])) # recherche action B
            pat_b = clean_val(r[f"patient_{sys_name}_phr_b"]) # recherche patient B

            # Couverture = au moins une action et in argument trouvés 
            couv = (act_a is not None and (agt_a or pat_a)) and (
                act_b is not None and (agt_b or pat_b) 
            )
            couverture.append(1 if couv else 0)

            #Invariance stricte = identité parfaite et pas de None
            strict = (
                (agt_a == agt_b)
                and (act_a == act_b)
                and (pat_a == pat_b)
                and all(x is not None for x in [agt_a, act_a, pat_a])
            )
            strict_matches.append(1 if strict else 0)

            # Invariance souple = tolérance sur omission - cas quand phrase perd agent 
            soft = (
                (act_a == act_b)
                and (agt_a is None or agt_b is None or agt_a == agt_b)
                and (pat_a is None or pat_b is None or pat_a == pat_b)
            )
            soft_matches.append(1 if soft else 0)

        df[f"{sys_name}_strict"] = strict_matches
        df[f"{sys_name}_soft"] = soft_matches

        ic_bas, ic_haut = ic(strict_matches)
        label = "spaCy (syntaxe)" if sys_name == "dep" else "AMRlib (sémantique)"
        print("test couverture - invariance")
        print(f"{label}")
        print(
            f"Inv strict : {np.mean(strict_matches)*100: .2f}%"
            f"({sum(strict_matches)}/ {n}) -- IC 95% : [{ic_bas :.1f}% - {ic_haut :.1f}%]"
            )
        print(f" Inv souple : {np.mean(soft_matches)*100 : .2f}%")
        print(f" couverture : {np.mean(couverture)*100 : .2f}%")

    # à faire - test témoin négatif

    # à faire -test stats McNemar

    # à faire - prévoire une sortie sur les paires où c'est en échec pour visualiser -




if __name__ == "__main__":
    path = "output/corpus_output.tsv"
    evaluate_pipeline(path)

