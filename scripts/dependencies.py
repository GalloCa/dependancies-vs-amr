"""
Module dependencies : définit la classe Dependencies, qui analyse une phrase
en dépendances avec spaCy, en extrait un triplet (agent, action, patient) et
fournit deux représentations de l'arbre : un dessin SVG (displaCy) et un texte
au format Conll
Ce module est importé par main.py ; il ne se lance pas tout seul.
"""

from spacy import displacy

class Dependencies:
    """
    Un objet qui représente une phrase analysée en dépendances

    Propriétés publiques :
        phrase : phrase (str) en lecture seule
        tree_image : le dessin de l'arbre de dépendances en texte SVG (str),
                     produit par displaCy, prêt pour la page HTML

    Méthodes publiques :
        to_conll    : ne reçoit rien ; renvoie l'arbre au format Conll (str) :
                      une ligne par token, colonnes séparées par des tabulations
                      (position du token, token, lemme, étiquette de dépendance,
                      gouverneur, position du gouverneur)
        find_root   : ne reçoit rien ; renvoie le token racine de self.doc
                      (étiquette ROOT), ou None si aucun token n'a cette étiquette
        find_child  : reçoit un token (le gouverneur) et une étiquette de dépendance (str) ;
                      renvoie le premier enfant direct du gouverneur avec cette
                      étiquette, ou None s'il n'y a pas de gouverneur ou si aucun
                      enfant a cette étiquette
        triplet_dep : ne reçoit rien ; renvoie un tuple (agent, action, patient) de
                      lemmes en minuscules (str). L'agent et le patient valent None
                      s'ils ne sont pas trouvés. Renvoie None si la phrase n'a pas de racine.
                      Actif  : agent = enfant "nsubj", patient = enfant "dobj" de la racine.
                      Passif : patient = enfant "nsubjpass" de la racine,
                               agent = enfant "pobj" de l'enfant "agent".

    Attributs privés:
        doc : objet Doc de spaCy, résultat de parsing de la phrase par spaCy
    """

    def __init__(self, phrase, nlp):
        self.phrase = phrase
        self.doc = nlp(phrase)
        self.tree_image = displacy.render(self.doc, style = "dep", jupyter=False)

    def to_conll(self):
        mots = []
        for w in self.doc:
            mots.append(f"{w.i+1}\t{w.text}\t{w.lemma_}\t{w.dep_}\t{w.head}\t{w.head.i+1}")
        return "\n".join(mots)

    def find_root(self):
        for w in self.doc:
            if w.dep_ == "ROOT":
                return w
        return None

    def find_child(self, gouverneur, etiq):
        if gouverneur is None:
            return None
        for i in gouverneur.children:
            if i.dep_ == etiq:
                return i
        return None

    def triplet_dep(self):
        gouverneur = self.find_root()
        if gouverneur is None:
            return None
        action = gouverneur.lemma_.lower()

        patient = self.find_child(gouverneur, "nsubjpass")
        if patient is None:
            agent = self.find_child(gouverneur, "nsubj")
            patient = self.find_child(gouverneur, "dobj")
        else:
            agent_first = self.find_child(gouverneur, "agent")
            agent = self.find_child(agent_first, "pobj")

        # !!! DECOMMENTER POUR TESTER PHRASES NEGATIVES !!!
        # no = self.find_child(gouverneur, "neg")
        # negation = no is not None

        if patient is not None:
            patient = patient.lemma_.lower()
        if agent is not None:
            agent = agent.lemma_.lower()

        return agent, action, patient # negation ----- !!! DECOMMENTER POUR TESTER PHRASES NEGATIVES !!!